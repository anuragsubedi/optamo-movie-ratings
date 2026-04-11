/**
 * Movie data models.
 *
 * TypeScript interfaces for the API response contracts.
 * Matches the shape defined in output_sample.json.
 */

export interface Movie {
  name: string;
  genre: string[];
  release_year: number | null;
  number_user_rated: number;
  average_rating: number;
}

/**
 * Paginated API response envelope.
 * All list endpoints (/top-rated, /search) return this shape.
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;     // total matching rows across all pages
  page: number;      // current 1-indexed page
  per_page: number;  // rows per page
  pages: number;     // total number of available pages
}

/**
 * Pagination and sort parameters forwarded to the backend.
 * Kept separate from SearchParams so the search-bar component
 * contract remains unchanged.
 */
export interface PageParams {
  page?: number;
  per_page?: number;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}

export interface SearchParams {
  name?: string;
  genre?: string;
  year?: number;
  rating?: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
}
