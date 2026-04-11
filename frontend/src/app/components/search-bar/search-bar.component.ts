import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { SearchParams } from '../../models/movie.model';

/**
 * Search bar component.
 *
 * Reusable filter form that emits SearchParams to the parent component.
 * Contains inputs for movie name, genre, year, and minimum rating.
 */
@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
  ],
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.scss'],
})
export class SearchBarComponent {
  @Output() search = new EventEmitter<SearchParams>();

  name = '';
  genre = '';
  year: number | null = null;
  rating: number | null = null;

  /** All genres available in the dataset. */
  genres: string[] = [
    'Action',
    'Adventure',
    'Animation',
    'Children',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Fantasy',
    'Film-Noir',
    'Horror',
    'IMAX',
    'Musical',
    'Mystery',
    'Romance',
    'Sci-Fi',
    'Thriller',
    'War',
    'Western',
  ];

  onSearch(): void {
    const params: SearchParams = {};

    if (this.name?.trim()) {
      params.name = this.name.trim();
    }
    if (this.genre) {
      params.genre = this.genre;
    }
    if (this.year) {
      params.year = this.year;
    }
    if (this.rating) {
      params.rating = this.rating;
    }

    this.search.emit(params);
  }

  onClear(): void {
    this.name = '';
    this.genre = '';
    this.year = null;
    this.rating = null;
    this.search.emit({});
  }
}
