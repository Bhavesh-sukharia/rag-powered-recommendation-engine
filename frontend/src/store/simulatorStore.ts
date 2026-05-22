import { create } from 'zustand';

// removed mock users import to load users from backend database
import { apiClient } from '@/lib/api';

const ACTIVE_USER_KEY = 'simulator.activeUserId';

import { EventLogItem } from '@/types/event';
import { Movie } from '@/types/movie';
import { Recommendation } from '@/types/recommendation';
import { User } from '@/types/user';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';
const USERS_API_BASE = API_BASE + '/api';
const MOVIES_API_BASE = API_BASE + '/api';
const MOVIES_PAGE_SIZE = 20;

interface BackendUser {
  id: string;
  username: string;
  preferred_genres?: string[];
  ratings?: Array<{ item_id?: number; rating_number?: number }>;
}

interface BackendRecommendation {
  movie: {
    item_id: number;
    title: string;
    genres?: string[];
    avg_rating?: number | null;
    sentiment_label?: string | null;
  };
  combined_score: number;
  cb_score?: number;
  cf_score?: number;
}

interface BackendMovie {
  id?: string;
  item_id?: number;
  title?: string;
  genres?: string[];
  overview?: string | null;
  avg_rating?: number | null;
  rating_number?: number | null;
  created_at?: string;
  sentiment_label?: string | null;
}

interface BackendMovieSearchResponse {
  movies?: BackendMovie[];
  page?: number;
  limit?: number;
  total?: number;
  has_more?: boolean;
  hasMore?: boolean;
}

function normalizeRatings(ratings: BackendUser['ratings']): Record<number, number> {
  return (ratings ?? []).reduce<Record<number, number>>((acc, rating) => {
    if (typeof rating.item_id === 'number' && typeof rating.rating_number === 'number') {
      acc[rating.item_id] = rating.rating_number;
    }
    return acc;
  }, {});
}

function mapUserFromApi(user: BackendUser, index: number): User {
  return {
    id: index + 1,
    apiId: user.id,
    name: user.username,
    tastes: user.preferred_genres ?? [],
    ratings: normalizeRatings(user.ratings),
    reviews: {},
  };
}

function mapMovieFromApi(movie: BackendMovie, index: number): Movie {
  const parsedId = movie.item_id ?? Number(movie.id);
  const id = Number.isFinite(parsedId) && parsedId > 0 ? parsedId : index + 1;

  return {
    id,
    item_id: movie.item_id ?? id,
    title: movie.title ?? 'Untitled movie',
    genres: movie.genres ?? [],
    overview: movie.overview ?? null,
    avg_rating: movie.avg_rating ?? null,
    rating_number: movie.rating_number ?? null,
    created_at: movie.created_at,
    sentiment_label: movie.sentiment_label ?? null,
  };
}

function buildFallbackRecommendations(
  catalogMovies: Movie[],
  weights: { cf: number; cb: number },
  options: { sentimentRerank: boolean; ragExplanation: boolean },
): Recommendation[] {
  const cfW = weights.cf / 100;
  const cbW = weights.cb / 100;

  return catalogMovies.map((movie) => {
    const cfBase = movie.cf_base ?? 0.75;
    const cfScore = +(cfBase * (0.85 + Math.random() * 0.15)).toFixed(2);
    const cbScore = +(0.72 + Math.random() * 0.25).toFixed(2);
    const sentimentScore = movie.sentiment ?? 0;
    const finalScore = +(
      cfScore * cfW + cbScore * cbW
    ).toFixed(3);

    return {
      movie,
      cfScore,
      cbScore,
      sentimentScore,
      finalScore,
      ragExplanation: options.ragExplanation
        ? `Because you like ${(movie.cb_tags ?? ['popular', 'well-reviewed'])[0]} and ${(movie.cb_tags ?? ['popular', 'well-reviewed'])[1]} movies.`
        : '',
    };
  }).sort((a, b) => b.finalScore - a.finalScore);
}

interface SimulatorStore {
  users: User[];
  movies: Movie[];
  isLoadingUsers: boolean;
  isLoadingMovies: boolean;
  isLoadingMoreMovies: boolean;
  isSearchingMovies: boolean;
  isLoadingMoreUsers: boolean;
  displayedMovieCount: number;
  movieSkip: number;
  movieSearchQuery: string;
  movieSearchPage: number;
  movieSearchLimit: number;
  movieSearchGenre: string;
  movieSearchSort: 'rating' | 'popularity' | 'title';
  hasMoreSearchMovies: boolean;
  activeUserId: number;
  recommendations: Recommendation[];
  activeTab: 'recommendations' | 'catalog' | 'users';
  events: EventLogItem[];
  pendingRating: { movieId: number; stars: number } | null;
  setActiveTab: (tab: SimulatorStore['activeTab']) => void;
  setActiveUser: (id: number) => void;
  weights: {
    cf: number;
    cb: number;
  };
  setWeights: (weights: { cf: number; cb: number }) => void;
  options: {
    sentimentRerank: boolean;
    ragExplanation: boolean;
  };
  setOptions: (options: Partial<SimulatorStore['options']>) => Promise<void>;
  filters: {
    genres: string[];
    minRating: number;
  };
  setFilters: (filters: Partial<SimulatorStore['filters']>) => void;
  toggleFilterGenre: (genre: string) => void;
  totalMovieCount: number;
  totalUserCount: number;
  userSkip: number;
  loadMovieCount: () => Promise<void>;
  loadUsers: () => Promise<void>;
  loadMoreUsers: () => Promise<void>;
  loadMovies: () => Promise<void>;
  loadMoreMovies: () => Promise<void>;
  searchMovies: (params: { query: string; page?: number; limit?: number; genre?: string; sort?: 'rating' | 'popularity' | 'title' }) => Promise<void>;
  loadMoreSearchMovies: () => Promise<void>;
  addUser: (name: string, tastes: string[]) => void;
  updateUser: (id: number, updates: Partial<User>) => void;
  selectRating: (movieId: number, stars: number) => void;
  confirmRating: () => void;
  discardRating: () => void;
  addReview: (movieId: number, text: string) => void;
  runRecommendations: () => void;
}

export const useSimulatorStore = create<SimulatorStore>((set, get) => ({
  users: [],
  movies: [],
  isLoadingUsers: false,
  isLoadingMoreUsers: false,
  isLoadingMovies: false,
  isLoadingMoreMovies: false,
  isSearchingMovies: false,
  displayedMovieCount: 20,
  movieSkip: 0,
  movieSearchQuery: '',
  movieSearchPage: 1,
  movieSearchLimit: MOVIES_PAGE_SIZE,
  movieSearchGenre: '',
  movieSearchSort: 'rating',
  hasMoreSearchMovies: false,
  activeUserId: (() => {
    try {
      if (typeof window !== 'undefined') {
        const saved = window.localStorage.getItem(ACTIVE_USER_KEY);
        return saved ? Number(saved) || 1 : 1;
      }
    } catch (e) {
      // ignore
    }
    return 1;
  })(),
  recommendations: [],
  activeTab: 'recommendations',
  pendingRating: null,
  weights: { cf: 50, cb: 50 },
  options: {
    sentimentRerank: true,
    ragExplanation: true,
  },
  loadMoreUsers: async () => {
    const state = get();

    if (state.isLoadingMoreUsers) {
      return;
    }

    set({ isLoadingMoreUsers: true });

    try {
      const response = await apiClient.get<{ users?: BackendUser[]; count?: number }>(`${USERS_API_BASE}/users`, {
        params: { skip: state.userSkip, limit: 20 },
      });

      const payload = response.data;
      const fetchedUsers = payload.users ?? [];

      if (!fetchedUsers.length) {
        set({ isLoadingMoreUsers: false, totalUserCount: payload.count ?? state.totalUserCount });
        return;
      }

      const moreUsers = fetchedUsers.map(mapUserFromApi);
      set({ users: [...state.users, ...moreUsers], userSkip: state.userSkip + moreUsers.length, isLoadingMoreUsers: false, totalUserCount: payload.count ?? state.totalUserCount });
    } catch (error) {
      set({ isLoadingMoreUsers: false });
      // eslint-disable-next-line no-console
      console.error('[users] Failed to load more users from backend', error);
    }
  },
  totalMovieCount: 0,
  totalUserCount: 0,
  userSkip: 0,
  filters: {
    genres: [],
    minRating: 0,
  },
  events: [],
  setWeights: (weights) =>
    set((state) => ({
      weights: {
        cf: weights.cf,
        cb: weights.cb,
      },
    })),
  setOptions: async (nextOptions) => {
    set((state) => ({ options: { ...state.options, ...nextOptions } }));
    try {
      const state = get();
      await apiClient.post('/api/config/options', {
        sentimentRerank: state.options.sentimentRerank,
        ragExplanation: state.options.ragExplanation,
      });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to persist options to backend', err);
    }
  },
  setFilters: (nextFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...nextFilters },
    })),
  toggleFilterGenre: (genre) =>
    set((state) => {
      const exists = state.filters.genres.includes(genre);
      return {
        filters: {
          ...state.filters,
          genres: exists
            ? state.filters.genres.filter((current) => current !== genre)
            : [...state.filters.genres, genre],
        },
      };
    }),
  loadUsers: async () => {
    set({ isLoadingUsers: true, userSkip: 0 });


    try {
      const response = await apiClient.get<{ users?: BackendUser[]; count?: number }>(`${USERS_API_BASE}/users`, {
        params: { skip: 0, limit: 20 }
      });

      const payload = response.data;
      const fetchedUsers = payload.users ?? [];


      if (!fetchedUsers.length) {
        set({ users: [], isLoadingUsers: false, totalUserCount: payload.count ?? 0, userSkip: 0 });
        return;
      }

      const users = fetchedUsers.map(mapUserFromApi);
      // Prefer saved active user from localStorage if available
      let previousActive = get().activeUserId;
      try {
        if (typeof window !== 'undefined') {
          const saved = window.localStorage.getItem(ACTIVE_USER_KEY);
          if (saved) previousActive = Number(saved) || previousActive;
        }
      } catch (e) {
        // ignore
      }

      const resolvedActive = users.some((user) => user.id === previousActive) ? previousActive : users[0].id;

      try {
        if (typeof window !== 'undefined') window.localStorage.setItem(ACTIVE_USER_KEY, String(resolvedActive));
      } catch (e) {
        // ignore
      }

      set({ users, activeUserId: resolvedActive, isLoadingUsers: false, userSkip: users.length, totalUserCount: payload.count ?? users.length });
    } catch (error) {
      set({ isLoadingUsers: false });
      // eslint-disable-next-line no-console
      console.error('[users] Failed to load users from backend', error);
    }
  },
  loadMovies: async () => {
    set({
      isLoadingMovies: true,
      movieSkip: 0,
      movieSearchQuery: '',
      movieSearchPage: 1,
      hasMoreSearchMovies: false,
      isSearchingMovies: false,
    });

    try {
      const response = await apiClient.get<BackendMovie[]>(`${MOVIES_API_BASE}/movies`, {
        params: { skip: 0, limit: MOVIES_PAGE_SIZE },
      });
      const payload = response.data;
      const movies = payload.map(mapMovieFromApi);

      set({ movies, isLoadingMovies: false, movieSkip: MOVIES_PAGE_SIZE });
      // update total count if backend provides it
      try {
        const cntResp = await apiClient.get<{ count: number }>(`${MOVIES_API_BASE}/movies/count`);
        const total = cntResp.data?.count ?? movies.length;
        set({ totalMovieCount: total });
      } catch (e) {
        // fallback: use loaded length
        set({ totalMovieCount: movies.length });
      }
    } catch (error) {
      set({ isLoadingMovies: false });
      // eslint-disable-next-line no-console
      console.error('Failed to load movies from backend', error);
    }
  },
  loadMovieCount: async () => {
    try {
      const cntResp = await apiClient.get<{ count: number }>(`${MOVIES_API_BASE}/movies/count`);
      const total = cntResp.data?.count ?? 0;
      set({ totalMovieCount: total });
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Failed to load movie count', e);
    }
  },
  loadMoreMovies: async () => {
    const state = get();
    if (state.isLoadingMoreMovies) return;

    set({ isLoadingMoreMovies: true });

    try {
      const response = await apiClient.get<BackendMovie[]>(`${MOVIES_API_BASE}/movies`, {
        params: { skip: state.movieSkip, limit: MOVIES_PAGE_SIZE },
      });

      const payload = response.data;

      if (payload.length === 0) {
        set({ isLoadingMoreMovies: false });
        return;
      }

      const newMovies = payload.map(mapMovieFromApi);
      set({
        movies: [...state.movies, ...newMovies],
        movieSkip: state.movieSkip + newMovies.length,
        isLoadingMoreMovies: false,
      });
      // try to refresh total after loading more
      try {
        const cntResp = await apiClient.get<{ count: number }>(`${MOVIES_API_BASE}/movies/count`);
        const total = cntResp.data?.count ?? (state.movies.length + newMovies.length);
        set({ totalMovieCount: total });
      } catch (e) {
        // ignore
      }
    } catch (error) {
      set({ isLoadingMoreMovies: false });
      // eslint-disable-next-line no-console
      console.error('Failed to load more movies from backend', error);
    }
  },
  searchMovies: async ({ query, page = 1, limit = MOVIES_PAGE_SIZE, genre = '', sort = 'rating' }) => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      await get().loadMovies();
      return;
    }

    set({
      isSearchingMovies: true,
      movieSearchQuery: trimmedQuery,
      movieSearchPage: page,
      movieSearchLimit: limit,
      movieSearchGenre: genre,
      movieSearchSort: sort,
      hasMoreSearchMovies: false,
      movieSkip: 0,
    });

    try {
      const response = await apiClient.get<BackendMovieSearchResponse>(`${MOVIES_API_BASE}/movies/search`, {
        params: {
          q: trimmedQuery,
          page,
          limit,
          genre: genre || undefined,
          sort,
        },
      });

      const payload = response.data;
      const fetchedMovies = (payload.movies ?? []).map(mapMovieFromApi);
      const resolvedPage = payload.page ?? page;
      const resolvedLimit = payload.limit ?? limit;
      const resolvedTotal = payload.total ?? fetchedMovies.length;
      const resolvedHasMore = payload.has_more ?? payload.hasMore ?? resolvedPage * resolvedLimit < resolvedTotal;

      set({
        movies: fetchedMovies,
        isSearchingMovies: false,
        movieSearchPage: resolvedPage,
        movieSearchLimit: resolvedLimit,
        movieSearchGenre: genre,
        movieSearchSort: sort,
        hasMoreSearchMovies: resolvedHasMore,
        totalMovieCount: resolvedTotal,
      });
    } catch (error) {
      set({ isSearchingMovies: false });
      // eslint-disable-next-line no-console
      console.error('Failed to search movies from backend', error);
    }
  },
  loadMoreSearchMovies: async () => {
    const state = get();
    if (state.isLoadingMoreMovies || state.isSearchingMovies || !state.movieSearchQuery.trim() || !state.hasMoreSearchMovies) {
      return;
    }

    const nextPage = state.movieSearchPage + 1;

    set({ isLoadingMoreMovies: true });

    try {
      const response = await apiClient.get<BackendMovieSearchResponse>(`${MOVIES_API_BASE}/movies/search`, {
        params: {
          q: state.movieSearchQuery,
          page: nextPage,
          limit: state.movieSearchLimit,
          genre: state.movieSearchGenre || undefined,
          sort: state.movieSearchSort,
        },
      });

      const payload = response.data;
      const newMovies = (payload.movies ?? []).map(mapMovieFromApi);
      const mergedMovies = [...state.movies, ...newMovies];
      const resolvedPage = payload.page ?? nextPage;
      const resolvedLimit = payload.limit ?? state.movieSearchLimit;
      const resolvedTotal = payload.total ?? mergedMovies.length;
      const resolvedHasMore = payload.has_more ?? payload.hasMore ?? resolvedPage * resolvedLimit < resolvedTotal;

      set({
        movies: mergedMovies,
        movieSearchPage: resolvedPage,
        movieSearchLimit: resolvedLimit,
        hasMoreSearchMovies: resolvedHasMore,
        isLoadingMoreMovies: false,
        totalMovieCount: resolvedTotal,
      });
    } catch (error) {
      set({ isLoadingMoreMovies: false });
      // eslint-disable-next-line no-console
      console.error('Failed to load more searched movies from backend', error);
    }
  },
  setActiveTab: (tab) => {
    set({ activeTab: tab });
    if (tab === 'recommendations') {
      // refresh recommendations when switching to the recommendations tab
      void get().runRecommendations();
    }
  },
  setActiveUser: (id) => {
    const state = get();
    set({
      activeUserId: id,
      pendingRating: null,
      events: [{ type: 'user', text: `Switched to user ${id}`, time: new Date().toLocaleTimeString() }, ...state.events],
    });
    try {
      if (typeof window !== 'undefined') window.localStorage.setItem(ACTIVE_USER_KEY, String(id));
    } catch (e) {
      // ignore
    }
    // Auto-run recommendations when user changes
    void state.runRecommendations();
  },
  addUser: (name, tastes) => {
    (async () => {
      try {
        // Create user in backend
        await apiClient.post(`${USERS_API_BASE}/users`, {
          username: name,
          preferred_genres: tastes,
          ratings: [],
        });

        // Refresh users from backend and select newly created user by name
        await get().loadUsers();
        const created = get().users.find((u) => u.name === name);
        if (created) {
          try {
            if (typeof window !== 'undefined') window.localStorage.setItem(ACTIVE_USER_KEY, String(created.id));
          } catch (e) {
            // ignore
          }
          set({ activeUserId: created.id, pendingRating: null });
        }

        const state = get();
        set({
          events: [
            {
              type: 'user',
              text: `Created new user: ${name}`,
              time: new Date().toLocaleTimeString(),
            },
            ...state.events,
          ],
        });
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to create user on backend', error);
      }
    })();
  },
  updateUser: (id, updates) => {
    const state = get();
    const targetUser = state.users.find((user) => user.id === id);
    const users = state.users.map((user) => (user.id === id ? { ...user, ...updates } : user));

    set({
      users,
      events: [
        {
          type: 'user',
          text: `Updated user ${updates.name ?? `#${id}`}`,
          time: new Date().toLocaleTimeString(),
        },
        ...state.events,
      ],
    });

    if (targetUser?.apiId) {
      const preferredGenres = updates.tastes ?? targetUser.tastes;

      void apiClient.put(`${USERS_API_BASE}/users/${targetUser.apiId}`, {
        preferred_genres: preferredGenres,
      }).catch((error) => {
        // eslint-disable-next-line no-console
        console.error('Failed to persist user preferences', error);
      });
    }
  },
  selectRating: (movieId, stars) => {
    set({ pendingRating: { movieId, stars } });
  },
  confirmRating: () => {
    const state = get();
    if (!state.pendingRating) return;

    const { movieId, stars } = state.pendingRating;
    const users = state.users.map((user) => {
      if (user.id !== state.activeUserId) return user;
      return {
        ...user,
        ratings: {
          ...user.ratings,
          [movieId]: stars,
        },
      };
    });

    set({
      users,
      pendingRating: null,
      events: [
        {
          type: 'rate',
          text: `Rated movie ${movieId} with ${stars} stars`,
          time: new Date().toLocaleTimeString(),
        },
        ...state.events,
      ],
    });

    const activeUser = state.users.find((user) => user.id === state.activeUserId);
    const userApiId = activeUser?.apiId;

    if (!userApiId) {
      return;
    }

    void apiClient.post(`${USERS_API_BASE}/users/${userApiId}/ratings`, {
      item_id: movieId,
      rating_number: stars,
    }).catch((error) => {
      // eslint-disable-next-line no-console
      console.error('Failed to persist rating update', error);
    });
  },
  discardRating: () => {
    set({ pendingRating: null });
  },
  addReview: (movieId, text) => {
    const state = get();
    const users = state.users.map((user) => {
      if (user.id !== state.activeUserId) return user;
      return {
        ...user,
        reviews: {
          ...user.reviews,
          [movieId]: text,
        },
      };
    });

    set({
      users,
      events: [
        {
          type: 'review',
          text: `Reviewed movie ${movieId}`,
          time: new Date().toLocaleTimeString(),
        },
        ...state.events,
      ],
    });
  },
  runRecommendations: async () => {
    const state = get();
    const activeUser = state.users.find((user) => user.id === state.activeUserId);
    const w = state.weights ?? { cf: 50, cb: 50 };
    const options = state.options ?? { sentimentRerank: false, ragExplanation: true };

    if (!activeUser) {
      set({ recommendations: [] });
      return;
    }

    try {
      const response = await apiClient.post<{ recommendations?: BackendRecommendation[] }>(
        `${USERS_API_BASE}/recommendations`,
        {
          username: activeUser.name,
          cb_weight: w.cb / 100,
          cf_weight: w.cf / 100,
          count: 20,
        },
      );

      const payload = response.data;
      const recommendations = (payload.recommendations ?? []).map((item) => {
        const title = item.movie.title;

        return {
          movie: {
            id: item.movie.item_id,
            title,
            genres: item.movie.genres ?? [],
            avg_rating: item.movie.avg_rating ?? null,
            sentiment_label: item.movie.sentiment_label ?? null,
          },
          cfScore: item.cf_score ?? 0,
          cbScore: item.cb_score ?? 0,
          finalScore: item.combined_score,
          ragExplanation: options.ragExplanation
            ? `Because you like ${title} and similar genres.`
            : '',
        };
      });

      set({
        recommendations,
        events: [
          {
            type: 'rec',
            text: 'Generated recommendations from API',
            time: new Date().toLocaleTimeString(),
          },
          ...get().events,
        ],
      });
      return;
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to fetch recommendations from backend, using fallback', error);
    }

    const recs = buildFallbackRecommendations(get().movies, w, options);

    set({
      recommendations: recs,
      events: [
        {
          type: 'rec',
          text: 'Generated recommendations',
          time: new Date().toLocaleTimeString(),
        },
        ...get().events,
      ],
    });
  },
}));
