import {Component, Input, OnInit} from '@angular/core';
import {Video} from "./model/video";
import {Router} from "@angular/router";

@Component({
  selector: 'app-video-card',
  templateUrl: './video-card.component.html',
  styleUrl: './video-card.component.scss'
})
export class VideoCardComponent implements OnInit {

  @Input()
  id:string ='';

  @Input()
  content: Video ={
    title: '',
    id: '',
    type: '',
    actors: '',
    directors: '',
    releaseDate: '',
    description: '',
    duration: '',
    genres: '',
  }

  ngOnInit(): void {
  }

  constructor(private router: Router) {
  }

  openVideo(): void {
    this.router.navigate(['/video', this.content?.id]);
  }

  getYear(): number {
    const date = new Date(this.content.releaseDate);
    return date.getFullYear();
  }
}
