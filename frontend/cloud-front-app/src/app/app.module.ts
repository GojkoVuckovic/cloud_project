import { NgModule } from '@angular/core';
import {BrowserModule, provideClientHydration, withNoHttpTransferCache} from '@angular/platform-browser';
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {LayoutModule} from "./layout/layout.module";
import {LoginRegisterModule} from "./login-register/login-register.module";
import {MatNativeDateModule} from "@angular/material/core";
import { DatePipe } from '@angular/common';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    LayoutModule,
    LoginRegisterModule,
    BrowserAnimationsModule,
    MatNativeDateModule
  ],
  providers: [
    provideAnimationsAsync(),
    provideClientHydration(withNoHttpTransferCache()),
    DatePipe
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
