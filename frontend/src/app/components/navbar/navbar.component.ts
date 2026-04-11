import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../services/auth.service';

/**
 * Navigation bar component.
 *
 * Displays the app title and a logout button.
 * Subscribes to auth state to show/hide the logout action.
 */
@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, MatToolbarModule, MatButtonModule, MatIconModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent {
  isAuthenticated$;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.isAuthenticated$ = this.authService.isAuthenticated$;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
