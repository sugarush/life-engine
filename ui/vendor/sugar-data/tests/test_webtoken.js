import WebToken from '../lib/webtoken.js';

import { HOST } from "./settings.js";

let expect = chai.expect;

describe('WebToken', () => {
  it('cannot authenticate without a url', async function() {
    try {
      await WebToken.authenticate();
    } catch {
      return null;
    }
    expect(false).not.to.be.false;
  });

  it('cannot authenticate without data', async function() {
    try {
      await WebToken.authenticate('http://invalid');
    } catch {
      return null;
    }
    expect(false).not.to.be.false;
  });

  it('can be unauthenticated', function() {
    expect(WebToken.authenticated).to.be.false;
  });

  it('can authenticate', async function() {
    let url = `${HOST}/v1/authentication`;
    let data = {
      data: {
        attributes: {
          username: 'admin',
          password: 'admin'
        }
      }
    };
    await WebToken.authenticate(url, data);
    expect(WebToken.token).not.to.be.null;
  });

  it('can be authenticated', function() {
    expect(WebToken.authenticated).to.be.true;
  });

  it('can refresh', async function() {
    let url = `${HOST}/v1/authentication`;
    let token = WebToken.token;
    await WebToken.refresh(url);
    expect(WebToken.token).not.to.be.null;
    expect(WebToken.token).not.to.equal(token);
  });

  it('can deauthenticate', async function() {
    await WebToken.deauthenticate();
    expect(WebToken.token).to.be.null;
  });

  it('can authenticate for the rest of the tests', async function() {
    let url = `${HOST}/v1/authentication`;
    let data = {
      data: {
        attributes: {
          username: 'admin',
          password: 'admin'
        }
      }
    };
    await WebToken.authenticate(url, data);
    expect(WebToken.token).not.to.be.null;
  });
});
