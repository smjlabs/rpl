$(function(){

    let _status = null
    let _interval = null
    let _done = false;

    $(document).on("click","#btnSearch",function(e){
        e.preventDefault()
        let _search_tag = $("#search")
        _search = _search_tag.val()
        
        _search_tag.removeClass('border border-danger')

        let _limit_tag = $("#limit")
        _limit = _limit_tag.val()
        
        if(_search.length > 0){
            
            $("#loading_progress").removeClass('d-none').find(".text-replace-temp").html("processing ... ")
            $("#loading_progress").find('.progress-bar').css({"width": '0%'});

            _interval = setInterval(checkLimit, 1000);
            processACM(_search)
        }else{
            _search_tag.addClass('border border-danger')
            _search_tag.focus()

        }

    })

    function checkLimit(){
        if(_status === 100){
            clearInterval(_interval);
            $("#loading_progress").addClass('d-none').find(".text-replace-temp").html("... ")
            $("#loading_progress").find('.progress-bar').css({"width": '0%'});
            _status = 0
            swal("Done!", "Scapping Process Done!", "success");

        }else{
            if(_done === false){
                getRecordACM()
            }
        }
    }

    function getRecordACM()
    {
        _done = true
        $.ajax({
            // 'async': false,
            'type': "GET",
            // 'global': false,
            'dataType': 'json',
            'url': "./../administrator/scrapping/get-total-db",
            'data': { 
                'keyword' : _search,
                'limit' : _limit
            },
            'success': function (data) {
                // console.log(data)
                _status = data.data
                $("#loading_progress").find('.progress-bar').css({"width": data.data+'%'});
                _done = false
            }
        })
    }

    function processACM(_search)
    {   
        $.ajax({
            // 'async': false,
            'type': "GET",
            // 'global': false,
            'dataType': 'json',
            'url': "./../administrator/scrapping/get-record",
            'data': {
                'keyword' : _search,
                'limit' : _limit
            },
            'success': function (data) {
                // console.log(data)
            }
        })
    }

});