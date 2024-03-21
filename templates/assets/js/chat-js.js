(function () {
   
   var Message;
   Message = function (arg) {
       this.text = arg.text, this.message_side = arg.message_side;
       this.draw = function (_this) {
           return function () {
               var $message;
               $message = $($('.message_template').clone().html());
               $message.addClass(_this.message_side).find('.text').html(_this.text);
               $('.messages').append($message);
               return setTimeout(function () {
                   return $message.addClass('appeared');
               }, 0);
           };
       }(this);
       return this;
   };

   $(function () {
       var getMessageText, message_side, sendMessage;
       message_side = 'right';
       getMessageText = function () {
           var $message_input;
           $message_input = $('.message_input');
           return $message_input.val();
       };

       sendMessage = function (text, msg_side) {

           var $messages, message;
           if (text.trim() === '') {
               return;
           }

           var sMsg = {"Message": $('.message_input').val(), 'cid': $("#cid__").val() }
           
           postData('send-message', sMsg)


           $('.message_input').val('');
           $messages = $('.messages');

          
           message = new Message({
               text: text,
               message_side: msg_side
           });
           message.draw();
           return $messages.animate({ scrollTop: $messages.prop('scrollHeight') }, 300);
       };

       $('.send_message').click(function (e) {
           return sendMessage( getMessageText(), 'right');
       });
       
       $('.message_input').keyup(function (e) {
           if (e.which === 13) {
               return sendMessage(getMessageText(), 'right');
           }
       });


       function postData(url, data) {
         const options = {
             method: 'POST',
             headers: {'Content-Type': 'application/json'},
             body: JSON.stringify(data),
         };
   
         fetch(url, options)
             .then(response => response.json()) 
             .then(result => {
               //console.log('POST request successful:', result);  
             })
             .catch(error => {
                 //console.error('Error during POST request:', error);
             });
      }

       //sendMessage('Hello Philip! :)');
       setInterval(function(){
         var cid = $('#cid__').val()
         var data = {"cid": cid}
   
         const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data),
        };
   
        fetch('get-message', options)
            .then(response => response.json()) 
            .then(result => {
                //console.log('POST request successful:', result);  
                if(result.Message){
                sendMessage(result['Message'], 'left')}
            })
            
      }, 3000)

      function countdownTimer(minutes) {
         
         // Calculate the target time by adding minutes to the current time
         let targetTime = new Date();
         targetTime.setMinutes(targetTime.getMinutes() + minutes);
     
         // Update the countdown every second
         let countdownInterval = setInterval(function() {
             let currentTime = new Date();
             let timeDifference = targetTime - currentTime;
     
             if (timeDifference <= 0) {
                 clearInterval(countdownInterval);
                 console.log("Countdown completed!");
             } else {
                 let remainingMinutes = Math.floor(timeDifference / (1000 * 60));
                 let remainingSeconds = Math.floor((timeDifference % (1000 * 60)) / 1000);
                 //console.clear();  // Clear console for better display
                 $("#dispute-btn").val(`${remainingMinutes}:${remainingSeconds}`)
                 if(remainingMinutes == 0){
                  $("#dispute-btn").text(`Dispute match`)
                  $("#dispute-btn").attr('disabled', false)
                  }
                 //console.log(`Time remaining: ${remainingMinutes} minutes and ${remainingSeconds} seconds`);
             }
         }, 1000);  // Update every second
     }
     var rT = $("#rT").val()
     var rT = parseInt(rT);
     if(rT == 0){
      $("#dispute-btn").text(`Dispute match`)
      $("#dispute-btn").attr('disabled', false)
      }
     countdownTimer(rT)

     $('#iwon').click(function(){
      const options = {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({"cid": $('#cid__').val()}),
     };
     fetch('iwon', options)
         .then(response => response.json()) 
         .then(result => { window.location.reload() })
   

     })

     $('#ilost').click(function(){
      const options = {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({"cid": $('#cid__').val()}),
     };
     fetch('ilost', options)
         .then(response => response.json()) 
         .then(result => { 
            window.location.reload()
          })
     })

     $('#dispute-btn').click(function(){
      const options = {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify({"cid": $('#cid__').val()}),
     };
     fetch('idispute', options)
         .then(response => response.json()) 
         .then(result => {  })
     })
     
       
   });
}.call(this)); 
