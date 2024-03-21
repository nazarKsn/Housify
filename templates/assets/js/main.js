document.addEventListener("DOMContentLoaded", function() {
  
   $("#create_challenge_btn").click(function(){
    
      $('#create_challenge_btn').attr('disabled', 'true')
      $('#create_ch_spinner').show()

      var platform = $("#platform").val()
      var game = $("#game").val() 
      var amount = $('#amount').val()
      var gm_user = $('#game-username').val()
      var rules = $('#rules').val()
      var EXT = $("#EXT").val()

      var info = {
         "platform": platform,
         "game": game,
         "gm_user": gm_user,
         "amount": amount,
         "rules": rules,
         "EXT": EXT,
      }
      
      const options = {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify(info),
     };
     fetch('create-challenge', options)
         .then(response => response.json()) 
         .then(result => { 
            if(result.error){
               setTimeout(function(){
                  $("#create-challenge-status").text(result['error'])
                  $('#create_challenge_btn').attr('disabled', false)
                  $('#create_ch_spinner').hide()
               },1000)
              
            }

            if (result.success){
               $("#create-challenge-status").text(result['success'])
               setTimeout(function(){
               window.location.replace('active-challenge') },2000)
            }
          })
      
   })


   $('#accept-challenge-btn').click(async function(){
      var cid = $('#cid_').val()
      var data = {"cid": cid}
      $("#accept-challenge-btn").attr('disabled', true)
      $("#accept-challenge-spinner").show()
      const options = {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify(data),
     };

     fetch('accept-challenge', options)
         .then(response => response.json()) 
         .then(result => {
            if (result.Error){
               $("#accept-err").text(result.Error)
               $("#accept-challenge-btn").attr('disabled', false)
               $("#accept-challenge-spinner").hide()
            }
            else if(result.Accepted){
               window.location.replace(`/chat-room?cid=${cid}`)
            }
             console.log(result);  
         })
         .catch(error => {
             console.error('Error during POST request:', error);
             $("#accept-challenge-btn").attr('disabled', false)
             $("#accept-challenge-spinner").hide()
         });


   })

   $('#cancel-challenge-btn').click(async function(){
      var cid = $('#cid_').val()
      var data = {"cid": cid, }

      const options = {
         method: 'POST',
         headers: {'Content-Type': 'application/json'},
         body: JSON.stringify(data),
     };

     fetch('cancel-challenge', options)
         .then(response => response.json()) 
         .then(result => {
            if (result.success){
               $("#accept-err").text(result['success'])
            }

           
           
         })
        


   })


   function postData(url, data){17
      const options = {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(data),
      };
      fetch(url, options)
          .then(response => response.json()) 
          .then(result => {  })
         
   }
   
  
   

});