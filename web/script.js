var $messages = $('.messages-content'),
  d, h, m,
  i = 0;

$(window).load(function () {
  $messages.mCustomScrollbar();
  setTimeout(function () {
    fakeMessage();
  }, 100);

  $('<div class="message loading new"><span></span></div>').appendTo($('.mCSB_container'));
  updateScrollbar();
      

  msg = "What product would you recommend me to Buy?. Answer to me with the * Highly Recommended: , * Recommended: , and * Not Recommended: . Show the list recommendations in a coherent text format with indentation and line breaks"
  $.ajax({
    url: '/chat',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ data: msg }),   
    success: function (response) {
      $('.message.loading').remove();
      console.log("Server response:", response);3

      response = "<ul> " + response + " </li></ul>";

      response = response.replace(/\*/g, '</li><li>');

      response = response.replace('</li>', '');
      response = "While you think, I recommend to you: " + response;
      $('<div class="message new">' + response + '</div>').appendTo($('.mCSB_container')).addClass('new');
      updateScrollbar();
    },
    error: function (error) {
      console.error("Error:", error);
    }
  });

});

function updateScrollbar() {
  $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
    scrollInertia: 10,
    timeout: 0
  });
}

function setDate() {
  d = new Date()
  if (m != d.getMinutes()) {
    m = d.getMinutes();
    $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
  }
}

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  }
  $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
  setDate();
  $('.message-input').val(null);
  updateScrollbar();
  $('<div class="message loading new"><span></span></div>').appendTo($('.mCSB_container'));
  updateScrollbar();
  $.ajax({
    url: '/chat',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ data: msg }),
    success: function (response) {
      $('.message.loading').remove();
      console.log("Server response:", response);
      $('<div class="message new">' + response + '</div>').appendTo($('.mCSB_container')).addClass('new');
      updateScrollbar();
    },
    error: function (error) {
      console.error("Error:", error);
    }
  });

}

$('.message-submit').click(function () {
  insertMessage();
});

$(window).on('keydown', function (e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
})

var Fake = [
  'Hi there, I\'m Makers Tech Chat Bot assistant, How can I Help You :D?',
  'Nice to meet you',
  'How are you?',
  'Not too bad, thanks',
  'What do you do?',
  'That\'s awesome',
  'Codepen is a nice place to stay',
  'I think you\'re a nice person',
  'Why do you think that?',
  'Can you explain?',
  'Anyway I\'ve gotta go now',
  'It was a pleasure chat with you',
  'Time to make a new codepen',
  'Bye',
  ':)'
]

function fakeMessage() {
  if ($('.message-input').val() != '') {
    return false;
  }
  $('<div class="message loading new"><span></span></div>').appendTo($('.mCSB_container'));
  updateScrollbar();

  setTimeout(function () {
    $('.message.loading').remove();
    $('<div class="message new">' + Fake[i] + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    updateScrollbar();
    i++;
  }, 1000 + (Math.random() * 20) * 100);

}




document.getElementById('chatBtn').addEventListener('click', function () {
  document.getElementById('dynamicContent').innerHTML = '<h2>Chat</h2><p>Esta es la sección de chat.</p>';
});

document.getElementById('dashboardBtn').addEventListener('click', function () {
  document.getElementById('dynamicContent').innerHTML = '<h2>Dashboard</h2><p>Esta es la sección de dashboard.</p>';
});





