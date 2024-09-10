import {Component, OnInit} from '@angular/core';
import {AuthenticationService} from "../../login-register/authentication.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent implements OnInit{

  userRole: string='';

  constructor(private authService: AuthenticationService, private router:Router) {}

  ngOnInit(): void {
    this.authService.userRoleState.subscribe((role) => {
        this.userRole = role;
      }
    );
    this.authService.getUserRole();
    console.log(this.userRole);
  }

  logout() {
    this.authService.logout();
  }
}
