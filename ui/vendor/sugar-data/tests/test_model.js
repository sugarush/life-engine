import WebToken from '../lib/webtoken.js';
import { Model } from '../lib/model.js';

import { HOST } from "./settings.js";

let expect = chai.expect;

describe('Model', () => {

  describe('cannot be constructed...', () => {

    it('without a host', (done) => {
      try {
        let model = new Model();
      } catch {
        done();
      }
      expect(true).to.be.false;
      done();
    });

    it('witout a uri', (done) => {
      try {
        let model = new Model({
          host: HOST
        });
      } catch {
        done();
      }
      expect(true).to.be.false;
      done();
    });

    it('without a type', (done) => {
      try {
        let model = new Model({
          host: HOST,
          uri: 'v1'
        });
      } catch {
        done();
      }
      expect(true).to.be.false;
      done();
    });
  });

  describe('can be constructed...', () => {

    it('with a host, uri and type', () => {
      let model = new Model({
        host: HOST,
        uri: 'v1',
        type: 'test'
      });
      expect(model._host).to.equal(HOST);
      expect(model._uri).to.equal('v1');
      expect(model._type).to.equal('test');
    });

    it('with attributes', () => {
      let model = new Model({
        host: HOST,
        uri: 'v1',
        type: 'test',
        attributes: {
          field: 'value'
        }
      });
      expect(model.attributes).to.deep.equal({ field: 'value' });
    });

    it('with an id', () => {
      let model = new Model({
        host: HOST,
        uri: 'v1',
        type: 'test',
        id: 'test'
      });
      expect(model.id).to.deep.equal('test');
    });

  });

  it('can set it\'s id', () => {
    let model = new Model({
      host: HOST,
      uri: 'v1',
      type: 'test'
    });
    model.id = 'test';
    expect(model.id).to.equal('test');
  });

  it('can get it\'s id', () => {
    let model = new Model({
      host: HOST,
      uri: 'v1',
      type: 'test'
    });
    model.id = 'test';
    expect(model.id).to.equal('test');
  });

  it('can construct it\'s uri', () => {
    let model = new Model({
      host: HOST,
      uri: 'v1',
      type: 'test',
      id: 'test'
    });
    expect(model.uri).to.equal('http://localhost:8001/v1/test/test');
  });

  it('can save new data', async function() {
    let user = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users'
    });
    user.attributes.username = 'test';
    user.attributes.password = 'test';
    user.attributes.groups = [ 'test' ];
    await user.save();
    expect(user.errors).to.have.lengthOf(0);
    await user.delete();
  });

  it('can save existing data', async function() {
    let user = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users'
    });
    user.attributes.username = 'test';
    user.attributes.password = 'test';
    user.attributes.groups = [ 'test' ];
    await user.save();
    user.attributes.username = 'abc';
    await user.save();
    expect(user.errors).to.have.lengthOf(0);
    expect(user.attributes.username).to.equal('abc');
    await user.delete();
  });

  it('can load data', async function() {
    let user_alpha = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users',
      attributes: {
        username: 'test',
        password: 'test',
        groups: [ 'test' ]
      }
    });
    await user_alpha.save();
    let user_beta = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users',
      id: user_alpha.id
    });
    await user_beta.load();
    expect(user_beta.attributes.username).to.equal('test');
    await user_alpha.delete();
    await user_beta.delete();
  });

  it('can load data with specified fields', async function() {
    let user_alpha = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users',
      attributes: {
        username: 'test',
        password: 'test',
        groups: [ 'test' ]
      }
    });
    await user_alpha.save();
    let user_beta = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users',
      id: user_alpha.id
    });
    await user_beta.load({ fields: { username: 1 } });
    expect(user_beta.attributes.username).to.equal('test');
    expect(user_beta.attributes.password).to.be.undefined;
    await user_alpha.delete();
    await user_beta.delete();
  });

  it('can delete data', async function() {
    let user = new Model({
      host: HOST,
      uri: 'v1',
      type: 'users',
    });
    user.attributes.username = 'test';
    user.attributes.password = 'test';
    user.attributes.groups = [ 'test' ];
    await user.save();
    await user.delete();
    expect(user.id).to.be.null;
  });

});
