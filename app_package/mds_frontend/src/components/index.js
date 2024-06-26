// main entry point for the React app, responsible for rendering the App component into the DOM

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

console.log('API URL:', process.env.REACT_APP_API_URL);

ReactDOM.render(<App />, document.getElementById('root'));
