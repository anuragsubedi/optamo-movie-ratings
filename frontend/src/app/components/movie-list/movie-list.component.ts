import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Movie, SearchParams } from '../../models/movie.model';
import { MovieService } from '../../services/movie.service';
import { SearchBarComponent } from '../search-bar/search-bar.component';

/**
 * Movie list component.
 *
 * Main page that displays top-rated movies in a sortable Material table.
 * Integrates the search bar for filtering and allows row clicks to
 * navigate to the movie detail view.
 */
@Component({
  selector: 'app-movie-list',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatSortModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatButtonModule,
    SearchBarComponent,
  ],
  templateUrl: './movie-list.component.html',
  styleUrls: ['./movie-list.component.scss'],
})
export class MovieListComponent implements OnInit {
  displayedColumns: string[] = [
    'name',
    'release_year',
    'genre',
    'average_rating',
    'number_user_rated',
  ];

  movies: Movie[] = [];
  isLoading = false;
  isSearchMode = false;
  errorMessage = '';

  constructor(
    private movieService: MovieService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTopRated();
  }

  /** Load top-rated movies (default view). */
  loadTopRated(): void {
    this.isLoading = true;
    this.isSearchMode = false;
    this.errorMessage = '';

    this.movieService.getTopRated().subscribe({
      next: (movies) => {
        this.movies = movies;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Failed to load movies. Is the backend running?';
        this.isLoading = false;
        console.error('Error loading top-rated movies:', err);
      },
    });
  }

  /** Handle search params from the search bar component. */
  onSearch(params: SearchParams): void {
    // If no params provided, revert to top-rated
    if (!params.name && !params.genre && !params.year && !params.rating) {
      this.loadTopRated();
      return;
    }

    this.isLoading = true;
    this.isSearchMode = true;
    this.errorMessage = '';

    this.movieService.searchMovies(params).subscribe({
      next: (movies) => {
        this.movies = movies;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'Search failed. Please try again.';
        this.isLoading = false;
        console.error('Error searching movies:', err);
      },
    });
  }

  /** Navigate to movie detail view. */
  onMovieClick(movie: Movie): void {
    this.router.navigate(['/movies', movie.name]);
  }

  /** Sort the table data. */
  onSort(sort: Sort): void {
    if (!sort.active || sort.direction === '') {
      return;
    }

    this.movies = [...this.movies].sort((a, b) => {
      const isAsc = sort.direction === 'asc';
      switch (sort.active) {
        case 'name':
          return compare(a.name, b.name, isAsc);
        case 'release_year':
          return compare(a.release_year ?? 0, b.release_year ?? 0, isAsc);
        case 'average_rating':
          return compare(a.average_rating, b.average_rating, isAsc);
        case 'number_user_rated':
          return compare(a.number_user_rated, b.number_user_rated, isAsc);
        default:
          return 0;
      }
    });
  }
}

function compare(a: string | number, b: string | number, isAsc: boolean): number {
  return (a < b ? -1 : 1) * (isAsc ? 1 : -1);
}
