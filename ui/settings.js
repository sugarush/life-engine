export const ENVIRONMENT = 'development';

export let API_HOST;
export let ENGINE_HOST;

switch(ENVIRONMENT) {
  case 'development':
    API_HOST = 'http://127.0.0.1:8001';
    ENGINE_HOST = 'ws://127.0.0.1:8000';
    break;
  case 'production':
    break;
}
