import React, { Component } from 'react';
import {Layer, Rect, Stage, Group} from 'react-konva';
import logo from './logo.svg';
import './App.css';
import MyRect from './MyRect';



class App extends Component {

  constructor(...args) {
      super(...args);
      this.onBalanceDataComp = this.onBalanceDataComp.bind(this);

      this.state = {
          data: ''
      };

    }

  componentWillMount() {
     //_connection.open();
     var self = this;
     var wsuri = "ws://192.168.1.37:8080/ws";

this._connection = new autobahn.Connection({
            url: wsuri,
            realm: "realm1"
         });
this._connection.onopen = function (session, details) {
    console.log("connection opened");


    session.subscribe('com.example.balance.data', this.onBalanceDataComp).then(
               function (sub) {
                  console.log('subscribed to topic com.example.balance.data');
               },
               function (err) {
                  console.log('failed to subscribe to topic com.example.balance.data', err);
               }
            );
 
  //_session = session;
 }.bind(this);

 this._connection.onclose = function (reason, details) {
            console.log("Connection lost: " + reason);
 }

  this._connection.open();
    
  }

  componentDidMount() {
      console.log("App componnentDidMount called");
      //this.onBalanceData = this.onBalanceData.bind(this);
      



    }

            onBalanceDataComp (args) {
               var balanceDataMessage = args[0];
               console.log("onBalanceDataComp event received with counter " + balanceDataMessage);
               var balanceData = JSON.parse(balanceDataMessage);
               this.setState({
                data: balanceData
                });
               console.log(this.state);
            }



  render() {
    return (
      <Stage width={700} height={700}>
       
            <MyRect connection={this._connection} balanceData={this.state.data}/>
        
      </Stage>
    );
  }
}

export default App;


