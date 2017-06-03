/**
 * Created by AntonS on 6/3/2017.
 */

function likePost(post_id, element) {

    $.ajax({
        type: 'post',
        url: '/like_post/',
        dataType: 'json',
        data: {
            'post_id': post_id
        },
        success: function(data) {
            // set liked style based whether user liked a post
            var classname = "glyphicon glyphicon-heart-empty";

            if (data.is_liked) {
                classname = "glyphicon glyphicon-heart";
            }
            element.children[0].className = classname;

            // update like count
            element.children[2].innerText = data.likes_count;
        },
        error: function(xhr, status, error){
            alert(xhr.responseText);
        }
    });

}
