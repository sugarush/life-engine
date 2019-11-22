export const state = () => ({
  messages: [ ]
})

export const mutations = {
  add(state, message) {
    message.timestamp = Date.now();
    if(!message.timeout) {
      message.timeout = 5;
    }
    state.messages.push(message);
  },
  remove(state, message) {
    state.messages = _.reject(state.messages, (_message) => {
      return message.id == _message.id;
    });
  },
  expire(state) {
    state.messages = _.reject(state.messages, (message) => {
      return Date.now() > message.timestamp + (message.timeout * 1000);
    });
  }
}
