
$(function(){
    $('#panel-btn-3').trigger('click');
});

$(function() {
    $(".selectpicker").selectpicker({
        noneSelectedText : '请选择'
    });

    $(window).on('load', function() {
        $('.selectpicker').selectpicker('val', '');
        $('.selectpicker').selectpicker('refresh');
    });

    // 下拉数据加载
    $.ajax({
        type : 'get',
        url :"/account-list/",
        dataType : 'json',
        success : function(datas) {//返回list数据并循环获取
            // var select = $("#account1");
            for (var i = 0; i < datas['account_list'].length; i++) {
                $("#account1").append("<option value='"+datas['account_list'][i]+"'>"
                    + datas['account_list'][i] + "</option>");
                $("#account2").append("<option value='"+datas['account_list'][i]+"'>"
                    + datas['account_list'][i] + "</option>");
            }

            $('.selectpicker').selectpicker('val', '');
            $('.selectpicker').selectpicker('refresh');
        }
    });
});


$('#datainput').click(function () {
    $('#panel1').removeClass('color_red');
    $('#panel1').show();
    $('#panel1').empty();
    var file_csv = document.getElementById('datacsv').files[0];
    var file_xlsx = document.getElementById('dataxlsx').files[0];
    var account1 = $('#account1').val();
    var fd = new FormData();
    fd.append('account1',account1);
    fd.append('file_csv',file_csv);
    fd.append('file_xlsx',file_xlsx);
    $('#panel1').html("上传中，请稍等&nbsp;&nbsp;<i class='fa fa-spinner fa-pulse'></i>");
    $.ajax({
        url:"/data-input/",
        type:'POST',
        data:fd,
        datatype: 'json',
        processData: false,  // tell jQuery not to process the data
        contentType: false,  // tell jQuery not to set contentType
        success:function (arg) {
            var err = arg['err'];
            if(err == 0){
                $('#panel1').html("<span class=\"glyphicon glyphicon-ok\" aria-hidden=\"true\"></span>");
                $('#panel1').show()
            }else if(err == -1){
                $('#panel1').text(arg['msg']);
                $('#panel1').addClass('color_red');
                $('#panel1').show()
            }
        }
    })
});


$('#dataparsing').click(function () {
    $('#panel2_1').removeClass('color_red');
    $('#panel2_1').show();
    $('#panel2_1').empty();
    var account2 = $('#account2').val();
    var fd = new FormData();
    fd.append('account2',account2);

    $('#panel2_1').html("解析中，请稍等&nbsp;&nbsp;<i class='fa fa-spinner fa-pulse'></i>");
    $.ajax({
        url:"/data-parsing/",
        type:'POST',
        data:fd,
        datatype: 'json',
        processData: false,  // tell jQuery not to process the data
        contentType: false,  // tell jQuery not to set contentType
        success:function (arg) {
            var err = arg['err'];
            if(err == 0){
                $('#panel2_1').html("<span class=\"glyphicon glyphicon-ok\" aria-hidden=\"true\"></span>");
                $('#panel2_1').show()
            }else if(err == -1){
                $('#panel2_1').text(arg['msg']);
                $('#panel2_1').addClass('color_red');
                $('#panel2_1').show()
            }
        }
    })
});




$('#datainput2').click(function () {
    $('#panel2_2').removeClass('color_red');
    $('#panel2_2').show();
    $('#panel2_2').empty();
    $('#panel2_2').html("<i class='fa fa-spinner fa-pulse'></i>");
    var chart_type = $('#chart_type').val();
    $.post("/data-auto-draw/",{'chart_type':chart_type}, function(res){
        if(res['err'] === 0){
            var test = window.location.pathname;
            if(test == '/'){
                window.location.reload();
            }
            $('#panel2_2').html("<span class=\"glyphicon glyphicon-ok\" aria-hidden=\"true\"></span>");
            $('#panel2_2').show()
        }else if(res['err'] === -1){
            $('#panel2_2').html(res['msg']);
            $('#panel2_2').addClass('color_red');
            $('#panel2_2').show()

        }
    })
});

$('#panel-btn-3').click(function () {
    $('#panel-btn-3').addClass('fa-spin');
    $.get("/sku-list-update/", function(res){
        console.log(res['msg']);
        if(res['err'] == 0 ){
            var sku_list = res['msg'];
            var htm = "";
            n = 0;
            for(var i=0;i<sku_list.length;i++){
                var m = parseInt(5*Math.random());
                if(n === m){
                    if(n === 4){
                        n = 0
                    }else {
                        n = m + 1
                    }
                }else {
                    n = m
                }
                if(  n === 0){
                    var temp_str = "<button type='button' class='btn btn-warning btn-xs btn-xs-mb'"+"onclick = select_sku('"+sku_list[i]+"')>"+sku_list[i]+"</button>"
                }
                else if( n === 1){
                    var temp_str = "<button type='button' class='btn btn-info btn-xs btn-xs-mb'"+"onclick = select_sku('"+sku_list[i]+"')>"+sku_list[i]+"</button>"
                }
                else if( n === 2){
                    var temp_str = "<button type='button' class='btn btn-success btn-xs btn-xs-mb'"+"onclick = select_sku('"+sku_list[i]+"')>"+sku_list[i]+"</button>"
                }
                else if( n === 3){
                    var temp_str = "<button type='button' class='btn btn-primary btn-xs btn-xs-mb'"+"onclick = select_sku('"+sku_list[i]+"')>"+sku_list[i]+"</button>"
                }
                else if( n === 4){
                    var temp_str = "<button type='button' class='btn btn-danger btn-xs btn-xs-mb'"+"onclick = select_sku('"+sku_list[i]+"')>"+sku_list[i]+"</button>"
                }

                htm += temp_str
            }
            $('#sku_list').html(htm)
        }
        else if(res['err'] == -1){
            var htm = "<span style = 'color:red' >请将数据解析后再试试刷新</sapn>";
            $('#sku_list').html(htm);
        }
        $('#panel-btn-3').removeClass('fa-spin');
    });
});

function select_sku(sku_name) {
    var sku_list = $('#sku_id').val();
    if(sku_list.length == 0){
        var new_sku_list = sku_name;
    }
    else {
        var new_sku_list = sku_list +','+sku_name;
    }
    $('#sku_id').attr('value',new_sku_list)
}


$('#sku_id_btn').click(function () {
    var v = $('#sku_id').val();
    $('#panel_span_4').html("<i class='fa fa-spinner fa-pulse'></i>")
    if(v == ''){
        $('#panel_span_4').html("<span style='color:red;'>请输入系列名</span>")
    }else {
        $.get("/choose-sku-draw/?sku_name_list="+v , function (res) {
            if(res['err'] == 0){
                if(res['err_sku_name'] == ''){
                    $('#panel_span_4').html("<a href='/sku-chart/'>构图成功</a>")
                }else if(res['sus_sku_name'] != ''){
                    $('#panel_span_4').html("<a href='/sku-chart/'>构图成功</a><br><span style='color: red'>无效系列名："+res['err_sku_name']+"</span>")
                }else {
                    $('#panel_span_4').html("<span style='color: red'>无效系列名："+res['err_sku_name']+"</span>")
                }
            }
        })
    }
});


$('#jsLoginBtn').click(function () {
    var username = $('#login_username').val();
    var pwd = $('#login_pwd').val();
    var fd = new FormData();
    fd.append('username',username);
    fd.append('password',pwd);

    $.ajax({
        url:"/users/login/",
        type:'POST',
        data:fd,
        datatype: 'json',
        processData: false,  // tell jQuery not to process the data
        contentType: false,  // tell jQuery not to set contentType
        success:function (arg) {
            var err = arg['err'];
            if(err == 0){
                window.location.reload();
                console.log('123123123')
            }else if(err == -1){
                console.log('false')
            }
        }
    })
});

