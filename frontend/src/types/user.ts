export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface UserRegistration {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserAuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}