$("#loginform").submit(function(e) {

    e.preventDefault();

    // validate form
    var $form = $(this), url = $form.attr( 'action' );

    var form_data = $(this).serialize();

    //This is the Ajax post.Observe carefully. It is nothing but details of where_to_post,what_to_post
    //Send data
     $.ajax({
           url : url,
           type : "POST",
           data : form_data,

     success : function(json) {
         if (json.type == "success") {
             // refresh page
             location.reload(true);
         }
         else {
             // show error message above form
             var $alert_elem = $("#login-alert");
             $alert_elem.show();
             $alert_elem.text(json.msg);

             // clean password
             $('#login-password').val('');
         }
     },
     error : function(xhr,errmsg,err) {
         console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
     }
     });
});

$("#signupform").submit(function(e) {

    e.preventDefault();

    // validate form
    var $form = $(this), url = $form.attr( 'action' );

    var form_data = $(this).serialize();
    var alert_elem = $("#signup-alert");
    var error_elem = $('#signup-critical')

    //This is the Ajax post.Observe carefully. It is nothing but details of where_to_post,what_to_post
    //Send data
     $.ajax({
           url : url,
           type : "POST",
           data : form_data,

     success : function(json) {
         if (json.type == "success") {
             // clean alert element
             alert_elem.text('');

             // print msg instead of form
             var $success_elem = $('#signup-success');
             $success_elem.show();

             $success_elem.text(json.msg);
             $form.hide();
         }
         else if (json.type == "error-validation") {
            // show error message above form

             alert_elem.text('');
             alert_elem.show();
             var $messages = json.msg;

            for(var field in $messages) {
                if ($messages.hasOwnProperty(field)) {
                    for (var ix in $messages[field]) {
                        alert_elem.append('<li>' + $messages[field][ix] + '</li>');
                    }
                }
            }
         }
         else if (json.type == "error-email") {
             // hide registration form
             $form.hide();
             alert_elem.hide();

             // show error message above form
             error_elem.show();
             error_elem.text(json.msg);

             // log full msg to console
             console.log(json["msg-error"]);
         }


     },
     error : function(xhr,errmsg,err) {
         console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
     }
     });
});