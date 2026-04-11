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
