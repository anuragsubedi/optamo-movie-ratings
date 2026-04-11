import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Movie, PageParams, PaginatedResponse, SearchParams } from '../models/movie.model';
import { environment } from '../../environments/environment';

/**
 * Movie data service.
 *
 * Provides methods for all movie-related API calls.
 * Both list methods return a PaginatedResponse envelope and accept an optional
 * PageParams argument for page number, page size, and sort configuration.
 */
@Injectable({
  providedIn: 'root',
})
export class MovieService {
  private readonly baseUrl = `${environment.apiUrl}/movies`;

  constructor(private http: HttpClient) {}

  /**
   * Fetch paginated movies with >10K ratings AND average rating > 4.0.
   *
   * @param pageParams - Optional pagination and sort overrides.
   *                     Defaults: page=1, per_page=25, sort_by=average_rating, sort_dir=desc
   */
  getTopRated(pageParams: PageParams = {}): Observable<PaginatedResponse<Movie>> {
    const params = this._buildPageParams(pageParams);
    return this.http.get<PaginatedResponse<Movie>>(`${this.baseUrl}/top-rated`, { params });
  }

  /**
   * Fetch detailed information for a single movie by name.
   * This endpoint is not paginated — it returns a single Movie object.
   */
  getMovieDetails(name: string): Observable<Movie> {
    const params = new HttpParams().set('name', name);
    return this.http.get<Movie>(`${this.baseUrl}/details`, { params });
  }

  /**
   * Search / filter movies by multiple optional parameters.
   * Returns a paginated response envelope.
   *
   * @param searchParams - Filter criteria (name, genre, year, rating).
   * @param pageParams   - Optional pagination and sort overrides.
   *                       Defaults: page=1, per_page=25, sort_by=name, sort_dir=asc
   */
  searchMovies(
    searchParams: SearchParams,
    pageParams: PageParams = {}
  ): Observable<PaginatedResponse<Movie>> {
    let params = this._buildPageParams(pageParams);

    if (searchParams.name) {
      params = params.set('name', searchParams.name);
    }
    if (searchParams.genre) {
      params = params.set('genre', searchParams.genre);
    }
    if (searchParams.year) {
      params = params.set('year', searchParams.year.toString());
    }
    if (searchParams.rating) {
      params = params.set('rating', searchParams.rating.toString());
    }

    return this.http.get<PaginatedResponse<Movie>>(`${this.baseUrl}/search`, { params });
  }

  /** Build HttpParams from a PageParams object, omitting undefined fields. */
  private _buildPageParams(pageParams: PageParams): HttpParams {
    let params = new HttpParams();
    if (pageParams.page      != null) params = params.set('page',     pageParams.page.toString());
    if (pageParams.per_page  != null) params = params.set('per_page', pageParams.per_page.toString());
    if (pageParams.sort_by   != null) params = params.set('sort_by',  pageParams.sort_by);
    if (pageParams.sort_dir  != null) params = params.set('sort_dir', pageParams.sort_dir);
    return params;
  }
}
