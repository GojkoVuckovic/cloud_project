import {Component, OnInit} from '@angular/core';
import {Video} from "../video-card/model/video";
import {FormControl} from "@angular/forms";
import {AuthenticationService} from "../../login-register/authentication.service";
import {Router} from "@angular/router";
import {isPlatformBrowser} from "@angular/common";

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrl: './home-page.component.scss'
})
export class HomePageComponent implements OnInit{

  searchText: string = '';
  videos: Video[] = []
  userRole: string='';
  constructor(private authService: AuthenticationService, private router:Router) {}

  onSubmit() {
    alert('beep boop');
  }

  ngOnInit(): void {
    this.authService.userRoleState.subscribe((role) => {
        this.userRole = role;
      }
    );
    this.authService.getUserRole();
    if(this.userRole==''){
      this.router.navigate(['/login'])
    }
    this.videos.push({
      actors: "neki",
      description: "jupii",
      directors: "direktori",
      duration: "100000",
      genres: "zanrovi",
      id: "1",
      releaseDate: "januar",
      title: "eden golan",
      type: "horor"
    });

    this.videos.push({
      actors: "neki",
      description: "jupii",
      directors: "direktori",
      duration: "100000",
      genres: "zanrovi",
      id: "1",
      releaseDate: "januar",
      title: "eden golan",
      type: "horor"
    });
    this.videos.push({
      actors: "neki",
      description: "jupii",
      directors: "direktori",
      duration: "100000",
      genres: "zanrovi",
      id: "1",
      releaseDate: "januar",
      title: "eden golan",
      type: "horor"
    });

  }

}
