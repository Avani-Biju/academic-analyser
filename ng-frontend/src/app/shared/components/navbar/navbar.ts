import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {
  toggleSidebar() {
    const sidebar = document.querySelector('.app-sidebar');
    if (sidebar) {
      sidebar.classList.toggle('open');
    }
  }
}
