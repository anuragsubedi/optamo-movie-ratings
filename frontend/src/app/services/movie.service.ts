import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Movie, SearchParams } from '../models/movie.model';
import { environment } from '../../environments/environment';

/**
 * Movie data service.
 *
 * Provides methods for all movie-related API calls.
 * Returns Observables — components should use the async pipe
 * to prevent memory leaks.
 */
@Injectable({
  providedIn: 'root',
})
export class MovieService {
  private readonly baseUrl = `${environment.apiUrl}/movies`;

  constructor(private http: HttpClient) {}

  /**
   * Fetch movies with >10K ratings AND average rating > 4.0.
   */
  getTopRated(): Observable<Movie[]> {
    return this.http.get<Movie[]>(`${this.baseUrl}/top-rated`);
  }

  /**
   * Fetch detailed information for a single movie by name.
   */
  getMovieDetails(name: string): Observable<Movie> {
    const params = new HttpParams().set('name', name);
    return this.http.get<Movie>(`${this.baseUrl}/details`, { params });
  }

  /**
   * Search/filter movies by multiple optional parameters.
   * Only includes params that have values to keep the URL clean.
   */
  searchMovies(searchParams: SearchParams): Observable<Movie[]> {
    let params = new HttpParams();

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

    return this.http.get<Movie[]>(`${this.baseUrl}/search`, { params });
  }
}
