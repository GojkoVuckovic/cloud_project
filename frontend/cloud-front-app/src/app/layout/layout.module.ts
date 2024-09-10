import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MaterialModule} from "../infrastructure/material.module";
import { NavbarComponent } from './navbar/navbar.component';
import {RouterLink} from "@angular/router";
import { VideoCardComponent } from './video-card/video-card.component';
import { HomePageComponent } from './home-page/home-page.component';
import {FormsModule} from "@angular/forms";
import { VideoDetailsComponent } from './video-details/video-details.component';

@NgModule({
  declarations: [
    NavbarComponent,
    VideoCardComponent,
    HomePageComponent,
    VideoDetailsComponent,
  ],
  imports: [
    CommonModule,
    MaterialModule,
    RouterLink,
    FormsModule
  ],
  exports: [
    NavbarComponent
  ]
})
export class LayoutModule { }
