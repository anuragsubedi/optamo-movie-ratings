import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { Movie, PageParams, SearchParams } from '../../models/movie.model';
import { MovieService } from '../../services/movie.service';
import { SearchBarComponent } from '../search-bar/search-bar.component';

/**
 * Movie list component.
 *
 * Main page displaying movies in a sortable, paginated Material table.
 *
 * Sorting and pagination are both resolved server-side:
 *  - Clicking a column header fires a new API call with sort params and
 *    always resets to page 1, so the user immediately sees the globally
 *    top/bottom results under the new ordering.
 *  - The MatPaginator drives page navigation via onPageChange(), which
 *    fires another API call with the updated page index.
 *  - All state (page, sort, search params) is funnelled through a single
 *    fetchMovies() method, keeping the data-loading logic in one place.
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
    MatPaginatorModule,
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

  // ── Data ────────────────────────────────────────────────────────────────
  movies: Movie[] = [];

  // ── Pagination state (MatPaginator is 0-indexed; API is 1-indexed) ──────
  totalCount  = 0;
  currentPage = 0;       // 0-indexed to match MatPaginator
  pageSize    = 25;
  pageSizeOptions = [10, 25, 50, 100];

  // ── Sort state ───────────────────────────────────────────────────────────
  sortBy:  string           = 'average_rating';
  sortDir: 'asc' | 'desc'  = 'desc';

  // ── UI state ─────────────────────────────────────────────────────────────
  isLoading    = false;
  isSearchMode = false;
  errorMessage = '';

  /** Last search params received from the search bar — persisted across page turns. */
  private lastSearchParams: SearchParams = {};

  constructor(
    private movieService: MovieService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTopRated();
  }

  // ── Public entry points ──────────────────────────────────────────────────

  /** Reset to top-rated view (also used by Retry / Show Top Rated buttons). */
  loadTopRated(): void {
    this.isSearchMode     = false;
    this.lastSearchParams = {};
    this.sortBy           = 'average_rating';
    this.sortDir          = 'desc';
    this.currentPage      = 0;
    this.fetchMovies();
  }

  /** Receive search params from the SearchBarComponent. */
  onSearch(params: SearchParams): void {
    const hasFilters = !!(params.name || params.genre || params.year || params.rating);

    if (!hasFilters) {
      this.loadTopRated();
      return;
    }

    this.isSearchMode     = true;
    this.lastSearchParams = params;
    this.sortBy           = 'name';
    this.sortDir          = 'asc';
    this.currentPage      = 0;   // always start at page 1 on a new search
    this.fetchMovies();
  }

  /**
   * Handle a sort-header click from MatSort.
   *
   * Sorting always resets to page 1 so the user immediately sees the
   * globally top/bottom values under the new ordering, rather than an
   * arbitrary mid-dataset slice.
   */
  onSort(sort: Sort): void {
    if (!sort.active || sort.direction === '') return;

    this.sortBy      = sort.active;
    this.sortDir     = sort.direction as 'asc' | 'desc';
    this.currentPage = 0;   // reset to page 1 on every sort change
    this.fetchMovies();
  }

  /** Handle a MatPaginator page event (page navigation or page-size change). */
  onPageChange(event: PageEvent): void {
    this.currentPage = event.pageIndex;
    this.pageSize    = event.pageSize;
    this.fetchMovies();
  }

  /** Navigate to the movie detail view. */
  onMovieClick(movie: Movie): void {
    this.router.navigate(['/movies', movie.name]);
  }

  // ── Private ──────────────────────────────────────────────────────────────

  /**
   * Centralised data-fetching method.
   *
   * Reads the current page/sort/search state and fires a single API call.
   * Both loadTopRated(), onSearch(), onSort(), and onPageChange() funnel
   * through here to avoid duplicated subscription logic.
   */
  private fetchMovies(): void {
    this.isLoading   = true;
    this.errorMessage = '';

    const pageParams: PageParams = {
      page:     this.currentPage + 1,  // convert 0-indexed → 1-indexed for the API
      per_page: this.pageSize,
      sort_by:  this.sortBy,
      sort_dir: this.sortDir,
    };

    const obs$ = this.isSearchMode
      ? this.movieService.searchMovies(this.lastSearchParams, pageParams)
      : this.movieService.getTopRated(pageParams);

    obs$.subscribe({
      next: (res) => {
        this.movies     = res.data;
        this.totalCount = res.total;
        this.isLoading  = false;
      },
      error: (err) => {
        this.errorMessage = this.isSearchMode
          ? 'Search failed. Please try again.'
          : 'Failed to load movies. Is the backend running?';
        this.isLoading = false;
        console.error('Error fetching movies:', err);
      },
    });
  }
}
