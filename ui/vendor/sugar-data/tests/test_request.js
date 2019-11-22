import { jsonapi } from '../lib/request.js';

import { HOST } from "./settings.js";

let expect = chai.expect;

let url = `${HOST}/v1/users`;

describe('JSON API Request', () => {

  it('can send a request', async function() {
    let json = await jsonapi(url);
    expect(json.meta.total).to.equal(1);
  });

  it('can specify query parameters', async function() {
    let json = await jsonapi(url, {
      params: {
        'page[offset]': 1
      }
    });
    expect(json.data.length).to.equal(0);
  });

  it('can specify a method and body', async function() {
    let json = await jsonapi(url, {
      method: 'POST',
      body: {
        data: {
          type: 'users',
          attributes: {
            username: 'test',
            password: 'test',
            groups: [ 'test' ]
          }
        }
      }
    });
    expect(json.data.id).not.to.be.undefined;
    let id = json.data.id;
    json = await jsonapi(`${url}/${id}`, {
      method: 'DELETE'
    });
  });
});
