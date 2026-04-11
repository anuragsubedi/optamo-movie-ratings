import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Movie } from '../../models/movie.model';
import { MovieService } from '../../services/movie.service';

/**
 * Movie detail component.
 *
 * Displays detailed information for a single movie.
 * Route: /movies/:name
 * Fetches data via MovieService.getMovieDetails().
 */
@Component({
  selector: 'app-movie-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './movie-detail.component.html',
  styleUrls: ['./movie-detail.component.scss'],
})
export class MovieDetailComponent implements OnInit {
  movie: Movie | null = null;
  isLoading = true;
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private movieService: MovieService
  ) {}

  ngOnInit(): void {
    const name = this.route.snapshot.paramMap.get('name');
    if (name) {
      this.loadMovie(name);
    } else {
      this.errorMessage = 'No movie name provided.';
      this.isLoading = false;
    }
  }

  private loadMovie(name: string): void {
    this.movieService.getMovieDetails(name).subscribe({
      next: (movie) => {
        this.movie = movie;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage =
          err.status === 404
            ? `Movie "${name}" not found.`
            : 'Failed to load movie details.';
        this.isLoading = false;
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/movies']);
  }

  /** Generate an array of filled/empty stars for visual rating. */
  getStars(): { filled: boolean }[] {
    if (!this.movie) return [];
    const stars = [];
    const rating = Math.round(this.movie.average_rating * 2) / 2;
    for (let i = 1; i <= 5; i++) {
      stars.push({ filled: i <= Math.floor(rating) });
    }
    return stars;
  }
}
