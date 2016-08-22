import React from 'react';
import {Layer, Rect, Stage, Group, Circle} from 'react-konva';


class MyRect extends React.Component {

    constructor(...args) {
      super(...args);
      this.state = {
        color: 'green',
        br: 0,
        tl: 0,
        tr: 0,
        bl: 0,
        total_weight: 0,
        connected: 'red',
        leftBar: 10,
        rightBar: 10
      };
      this._connection = this.props.connection;
      this._session = this.props.session;
      //this._session = null;
      this.handleClick = this.handleClick.bind(this);
      this.handleClickDisconnect = this.handleClickDisconnect.bind(this);
      this.onBalanceData = this.onBalanceData.bind(this);
      this.callBalance = this.callBalance.bind(this);
      this.balanceResponse = this.balanceResponse.bind(this);
      this.callBalanceDisconnect = this.callBalanceDisconnect.bind(this);
      this.handleCircleClick = this.handleCircleClick.bind(this);

            // for debugging

      

    }

    componentDidMount() {
      console.log("componnentDidMount called");
      



    }

    componentWillReceiveProps(nextProps) {
        console.log("componentWillReceiveProps MyRect: ");
        console.log(nextProps);
        // left side tl -top , br - botton
        // 1) get gotal left weight tl + br
        var totalLeftWeight = nextProps.balanceData.tl + nextProps.balanceData.br;
        var totalRightWeight = nextProps.balanceData.tr + nextProps.balanceData.bl;
        var lefTopPercent = (nextProps.balanceData.tl * 100) / totalLeftWeight;
        var leftBottonPercent = (nextProps.balanceData.br * 100) / totalLeftWeight;
        var rightBottonPercent = (nextProps.balanceData.bl * 100) / totalRightWeight;
        var leftTop = Math.round((10 + leftBottonPercent));
        var rightTop = Math.round((10 + rightBottonPercent));
        this.setState({leftBar: leftTop});
        this.setState({rightBar: rightTop});

    }

    onBalanceData(args) {
               var balanceData = args[0];
               console.log("onBalanceData event received with counter " + balanceData);

    }

    balanceResponse(res){
              console.log("callBalance() result:", res);


 

    }

    callBalance(){
               console.log("callBalance() waiting for board connection");
               this._connection.session.call('com.example.balance', [1, 18]).then(
                  function (res) {

                     console.log("callBalance() result:", res);
                  },
                  function (err) {
                     console.log("callBalance() error:", err);
                  }
               );

              
            }

    callBalanceDisconnect(){
               this._connection.session.call('com.example.balance.disconnect').then(
                  function (res) {
                     console.log("callBalanceDisconnect() result:", res);
                  },
                  function (err) {
                     console.log("callBalanceDisconnect() error:", err);
                  }
               );

               
            }

    handleClick() {
      this.setState({
        color: Konva.Util.getRandomColor()
      });

      this.callBalance();
    } 

    handleClickDisconnect() {

      this.callBalanceDisconnect();
    } 

    handleCircleClick(){
      if (this.state.connected == 'red'){
        // todo make it goi into orange and wait for cennoction recived to change it
        // new state 
        
        this.callBalance();
        this.setState({connected: 'green'});
        

      }
      else if (this.state.connected == 'green'){
        
        this.callBalanceDisconnect();
         this.setState({connected: 'red'});
         // todo hanndle unsubscribe
       
      }

    }



    render() {
        return (
          <Layer>
            <Rect
                x={10} y={10} width={50} height={50}
                ref="top_left_rect"
                fill={this.state.color}
                shadowBlur={10}
                onClick={this.handleClick}
            />


            <Rect
                x={100} y={10} width={50} height={50}
                ref="top_right_rect"
                fill={this.state.color}
                shadowBlur={10}
                onClick={this.handleClick}
            />

            <Rect
                x={10} y={60} width={50} height={50}
                ref="botton_left_rect"
                fill={this.state.color}
                shadowBlur={10}
                onClick={this.handleClick}
            />

            <Rect
                x={100} y={60} width={50} height={50}
                ref="botton_right_rect"
                fill={this.state.color}
                shadowBlur={10}
                onClick={this.handleClick}
            />

            <Rect
                x={10} y={this.state.leftBar} width={50} height={5}
                ref="left_bar"
                fill='red'
                shadowBlur={1}
                onClick={this.handleClick}
            />

            <Rect
                x={100} y={this.state.rightBar} width={50} height={5}
                ref="right_bar"
                fill='red'
                shadowBlur={1}
                onClick={this.handleClick}
            />

            <Circle
              x= {190} y= {20}
              radius= {10}
              ref='connect_circle'
              fill= {this.state.connected}
              stroke= 'black'
              strokeWidth= {1}
              onClick={this.handleCircleClick}
            />
          </Layer>
        );
    } 

}

export default MyRect;