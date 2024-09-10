import { Component } from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import { DatePipe } from '@angular/common';
import {AuthenticationService} from "../authentication.service";


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent {
  registerForm: FormGroup = new FormGroup( {
    email : new FormControl('', Validators.required),
    password : new FormControl('', Validators.required),
    name : new FormControl('', Validators.required),
    surname : new FormControl('', Validators.required),
    username : new FormControl('', Validators.required),
    date : new FormControl('',Validators.required)
  });

  constructor(private datePipe: DatePipe,private authService: AuthenticationService) {}

  onSubmit(){
    this.authService.register(
      this.registerForm.controls['username'].value,
      this.registerForm.controls['email'].value,
      this.registerForm.controls['password'].value,
      this.datePipe.transform(this.registerForm.controls['date'].value, 'dd/MM/yyyy')!,
      this.registerForm.controls['name'].value,
      this.registerForm.controls['surname'].value
    )
  }

}
