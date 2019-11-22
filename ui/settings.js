export const ENVIRONMENT = 'development';

export let API_URI;
export let ENGINE_URI;

switch(ENVIRONMENT) {
  case 'development':
    API_URI = 'http://127.0.0.1:8001';
    ENGINE_URI = 'ws://127.0.0.1:8000';
    break;
  case 'production':
    break;
}
