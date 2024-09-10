import {Component, OnInit} from '@angular/core';
import {VideoDetails} from "../video-card/model/video-details";

@Component({
  selector: 'app-video-details',
  templateUrl: './video-details.component.html',
  styleUrl: './video-details.component.scss'
})
export class VideoDetailsComponent implements OnInit{
  videoId: string = '';
  videoSource: string = '';
  userRole: string = '';

  contentDetails: VideoDetails = {
    id: '',
    type: '',
    title: 'Some title goes here',
    actors: ['Pera Peric', 'Neko Drugi', 'Neko Treci'],
    directors: ['Misa Misic', 'Zdera Zderic'],
    releaseDate: '',
    description: 'Some desc goes here and it describes movie/content/tvoshow',
    duration: '',
    genres: ['Horror', 'Comedy', 'Action'],
  }

  constructor() {
  }

  ngOnInit(): void {
  }

  getStream(){

  }

  rateContent(rate: number){

  }

  subscribe(name: string, type: string) {
    console.log(name, type);
  }

  download() {

  }
}
