const functions = require('firebase-functions');
const admin = require('firebase-admin');

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions
//
var config = {
    apiKey: "AIzaSyA4s65NGcz_9EfKiPmfFKmN9brXwYR7BcU",
    authDomain: "track-a-bull.firebaseapp.com",
    databaseURL: "https://track-a-bull.firebaseio.com",
    projectId: "track-a-bull",
    storageBucket: "track-a-bull.appspot.com",
    messagingSenderId: "819088197621"
};

admin.initializeApp(config);

let interactionsDb = admin.database().ref('/Interactions/');
let itemsDb = admin.database().ref('/Items/');