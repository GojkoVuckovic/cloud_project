import { Injectable } from '@angular/core';
import {
  AuthenticationDetails,
  CognitoUser, CognitoUserAttribute,
  CognitoUserPool,
} from "amazon-cognito-identity-js";
import {Router} from "@angular/router";
import {environments} from "../../environments/environments";
import {BehaviorSubject, from, Observable} from "rxjs";
import {isPlatformBrowser} from "@angular/common";

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {

  private poolData = {
    UserPoolId: environments.cognitoUserPoolId,
    ClientId: environments.cognitoAppClientId,
  }
  private userPool: CognitoUserPool = new CognitoUserPool(this.poolData);

  cognitoUser: any;
  username: string = "";
  userId: BehaviorSubject<string> = new BehaviorSubject("");
  userRole$: BehaviorSubject<string> = new BehaviorSubject("");
  userRoleState: Observable<string> = this.userRole$.asObservable();


  constructor(private router: Router) {}

  login(email: any, password: any) {
    let authDetails: AuthenticationDetails = new AuthenticationDetails({
      Username: email,
      Password: password
    });
    this.username = email;
    let userData = {Username: email, Pool: this.userPool} ;
    const cognitoUser = new CognitoUser(userData);

    cognitoUser.authenticateUser(authDetails, {
      onSuccess: (session: any) => {
        this.cognitoUser = cognitoUser;

        const payload = this.cognitoUser.getSignInUserSession().getIdToken().decodePayload();
        const role = payload['custom:isAdmin'];
        if (role == "true") {
          localStorage.setItem('userRole', "Admin");
          this.userRole$.next("Admin");
        } else if (role == "false") {
          localStorage.setItem('userRole', "User");
          this.userRole$.next("User");
        }


        this.getUsersAttributes(this.cognitoUser).then((userAttributes: CognitoUserAttribute[]) => {
          console.log(userAttributes);
          const id = userAttributes.find(attr => attr.getName() === 'sub')?.getValue();
          if(id) localStorage.setItem('userId', id);

        });
        this.router.navigate(['/']);
      },
      newPasswordRequired: () => {
        alert("this page is yet to be made")
      },
      onFailure: (err) => {
        alert(err.message);
      }
    });
  }

  getUsersAttributes(cognitoUser: CognitoUser | null): Promise<any> {

    if(!cognitoUser) {
      return Promise.resolve(null)
    }

    return new Promise<CognitoUserAttribute[] | undefined>((resolve, reject) => {
      cognitoUser.getUserAttributes((err, attributes) => {
        if (err){
          reject(err);
          return;
        }
        resolve(attributes);
      });
    });
  }

  getUserId(){
    const id = localStorage.getItem('userId');
    if(id) return id;
    return '';
  }

  getCurrentUser(): CognitoUser | null {
    return this.userPool.getCurrentUser();
  }

  getUserRole() {
    if (typeof localStorage !== 'undefined') {
      const storedRole = localStorage.getItem("userRole");
      if (!storedRole) return;
      this.userRole$.next(storedRole);
    }
  }

  logout() {
    this.userPool = new CognitoUserPool(this.poolData);
    this.cognitoUser = this.userPool.getCurrentUser();
    this.userRole$.next('');
    this.userId.next('');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');

    if(this.cognitoUser){
      this.cognitoUser.signOut();
      this.router.navigate(['login']);
    }
  }

  register(username: string, email: string,
           password: string, birthdate: string,
           firstName: string, lastName: string, ) {

    const attributeList: CognitoUserAttribute[] = [
      new CognitoUserAttribute({Name:'email', Value:email}),
      new CognitoUserAttribute({Name:'given_name', Value:firstName}),
      new CognitoUserAttribute({Name:'family_name', Value:lastName}),
      new CognitoUserAttribute({Name:'birthdate', Value:birthdate})
    ];

    this.userPool.signUp(username, password, attributeList, [], (err, result)=>{
      if(err){
        alert(`Registration failed: ${err.message}`);
      } else {
        alert("Registration successful");
        this.router.navigate(['/login']);
      }
    });
  }
  getAccessToken() {
    let currentUser = this.userPool.getCurrentUser();
    if(!currentUser){
      console.log('error!');
      return from('');
    } else {
      return from(
        new Promise((resolve, reject) => {
          currentUser?.getSession((err: any, session: any) => {
            if(err){
              reject(err);
            } else if (!session?.isValid()){
              resolve(null);
            } else {
              // Change to access token if needed
              resolve(session?.getAccessToken().getJwtToken());
            }
          })
        })
      );
    }
  }



}
