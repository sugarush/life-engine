import { urlencode } from '../lib/urlencode.js';

let expect = chai.expect;

describe('URLEncode', () => {
  it('can encode a single value', () => {
    let result = urlencode({ test: 'value' });
    expect(result).to.equal('?test=value');
  });

  it('can encode multiple values', () => {
    let result = urlencode({ test: 'value', abc: 123 });
    expect(result).to.equal('?test=value&abc=123');
  });

  it('can encode JSON', () => {
    let result = urlencode({ test: JSON.stringify({ abc: 123 }) });
    expect(result).to.equal('?test=%7B%22abc%22:123%7D');
  })
});
