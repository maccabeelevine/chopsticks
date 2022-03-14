$( document ).ready(function() {
    console.log( "ready!" );
    initListeners();
    reloadState();
});

function reloadState() {
    console.log("reloading state");
    $.ajax({
        "url": "/state",
        "success": function(data, status, xhr) {
            let state = $.parseJSON(data.state);
            console.log("state");
            console.log(state);

            let last_move = $.parseJSON(data.last_move);

            updatePage(state, last_move);
        },
        "error": function(xhr, status, error) {
            console.error("error", xhr);
        }
    });
}

function initListeners() {
    $(".player_left .hit_left").on("click", function() {
        hit(2, 1, 1);
    });
    $(".player_left .hit_right").on("click", function() {
        hit(2, 1, 2);
    });
}

function hit(target, source_hand, target_hand) {
    move(['h', target, source_hand, target_hand].join());
}

function move(move) {
    $.ajax({
        "url": "/move",
        "contentType" : "text/plain",
        "data": move,
        "method": "POST",
        "success": function(data, status, xhr) {
            console.log("success posting move");
            reloadState();
            $("footer.status").text("ThetaBot is thinking...");
            setTimeout(function() { 
                botMove();
            }, 5000);
        },
        "error": function(xhr, status, error) {
            console.error("error", xhr);
        }
    });
}

function botMove() {
    $.ajax({
        "url": "/botMove",
        "method": "POST",
        "success": function(data, status, xhr) {
            console.log("success requesting a bot move");
            reloadState();
        },
        "error": function(xhr, status, error) {
            console.error("error", xhr);
        }
    });
}

function updatePage(state, last_move) {
    updatePlayer($(".human"), state._players[0]);
    updatePlayer($(".bot"), state._players[1]);
    updateLastMove(last_move);
}

function updatePlayer(sectionElement, player) {
    updateHand(1, sectionElement, player);
    updateHand(2, sectionElement, player);
}

function updateHand(hand, sectionElement, player) {
    let fingers = player._hands[hand-1].alive_fingers;
    $(".hands .hand:nth-child("+hand+")", sectionElement).text(fingers)
}

function updateLastMove(last_move) {
    if (last_move == null) {
        $("footer.status").text("Make the first move!");
    }
    else {
        $("footer.status").text("Last move: " + last_move);
    }
}