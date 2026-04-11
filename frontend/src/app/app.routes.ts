import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { LoginComponent } from './components/login/login.component';
import { MovieListComponent } from './components/movie-list/movie-list.component';
import { MovieDetailComponent } from './components/movie-detail/movie-detail.component';

/**
 * Application routes.
 *
 * - /login           → LoginComponent (public)
 * - /movies          → MovieListComponent (guarded)
 * - /movies/:name    → MovieDetailComponent (guarded)
 * - **               → redirect to /movies
 */
export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'movies',
    canActivate: [authGuard],
    children: [
      { path: '', component: MovieListComponent },
      { path: ':name', component: MovieDetailComponent },
    ],
  },
  { path: '', redirectTo: '/movies', pathMatch: 'full' },
  { path: '**', redirectTo: '/movies' },
];
