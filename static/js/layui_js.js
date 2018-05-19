layui.use(['laydate','form','table'], function(){
    var laydate = layui.laydate
        ,form = layui.form
        ,table = layui.table
    ;

    // 日期范围选择器
    laydate.render({
        elem: '#privot_date' //指定元素
        ,type: 'datetime' // 日期范围选择器
        ,range: true //   范围选择
        // ,min: -30 // 过去30天
        ,format: 'yyyy-MM-dd'
    });

    //表格
    var tableIns = table.render({
        elem: '#pivot_table'
        // ,height: 800
        ,url: '/pivot-table-data/' //数据接口
        ,page: true //开启分页
        ,limit: 15
        ,cols: [[ //表头
            {field: 'type', title: '类型', width:'14%', sort: true, fixed: 'left', style:'cursor:pointer',event:'skip'}
            ,{field: 'order_number', title: '销售数量', width:'14%', sort: true}
            ,{field: 'order_amount', title: '销售金额', width:'14%', sort: true}
            ,{field: 'refund_number', title: '退款数量', width:'14%', sort: true}
            ,{field: 'refund_amount', title: '退款金额', width: '14%', sort: true}
            ,{field: 'refund_rate', title: '退款率', width: '14%', sort: true}
            ,{field: 'freight_cost', title: '运费成本', width: '14%', sort: true}
        ]]
        ,id:'pivot_table'
        ,done:function (res,curr,count) {
            pivot_table_html()
        }
    });


    $.ajax({
        type: 'get',
        url: "/account-list/",
        dataType: 'json',
        success: function (datas) {//返回list数据并循环获取
            for (var i = 0; i < datas['account_list'].length; i++) {
                $("#privot_account").append("<option value='" + datas['account_list'][i] + "'>"
                    + datas['account_list'][i] + "</option>");}
            form.render('select');

        }});

    //监听提交
    form.on('submit(formDemo)', function(data){
        tableIns.reload({
            where:{
                'account':data.field.account
                ,'category':data.field.category
                ,'date':data.field.date
                ,'style':data.field.style
                ,'color':data.field.color
                ,'size':data.field.size
            }
            ,page:{
                curr:1
            }
            ,done:function (res,curr,count) {
                pivot_table_html()
            }
        });

        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });



    //监听单元格事件
    table.on('tool(table)', function(obj){

        var array = new Array();
        $('#privot_category option').each(function () {
            var txt = $(this).val()
            if(txt !== ''){
                array.push(txt)
            }
        });


        var data = obj.data;
        var table_category = data.类型;
        var table_account = $('#privot_account').val();
        var table_date = $('#privot_date').val();
        var table_style = $('#privot_style').val();
        var table_color = $('#privot_color').val();
        var table_size = $('#privot_size').val();
        // 判断选中的值是品类还是sku
        if($.inArray(table_category,array) !== -1){
            tableIns.reload({
                where:{
                    'account':table_account
                    ,'category':table_category
                    ,'date':table_date
                    ,'style':table_style
                    ,'color':table_color
                    ,'size':table_size
                }
                ,page:{
                    curr:1
                }
                ,done:function (res,curr,count) {
                    pivot_table_html()
                }
            });
        }else {
            tableIns.reload({
                where:{
                    'account':table_account
                    ,'category':$('#privot_category').val()
                    ,'date':table_date
                    ,'style':table_category
                    ,'color':table_color
                    ,'size':table_size
                }
                ,page:{
                    curr:1
                }
                ,done:function (res,curr,count) {
                    pivot_table_html()
                }
            });
        }

    });


    form.on('select(account)', function(data){
        console.log(data.value); //得到被选中的值
        account = data.value;
        $("#privot_style").empty().append("<option value='.*'>选择style</option>");
        $.ajax({
            type: 'get',
            url: "/style_list/?account="+account ,
            dataType: 'json',
            success: function (datas) {//返回list数据并循环获取
                for (var i = 0; i < datas['data_style'].length; i++) {
                    $("#privot_style").append("<option value='" + datas['data_style'][i] + "'>"
                        + datas['data_style'][i] + "</option>");}

                form.render('select');
            }});
    });


    form.on('select(style)', function(data){
        console.log(data.value); //得到被选中的值
        style = data.value;
        $("#privot_color").empty().append("<option value='.*'>选择color</option>");
        $("#privot_size").empty().append("<option value='.*'>选择size</option>");

        $.ajax({
            type: 'get',
            url: "/color_size_list/?account="+account +'&style=' + style,
            dataType: 'json',
            success: function (datas) {//返回list数据并循环获取
                for (var i = 0; i < datas['data_color'].length; i++) {
                    $("#privot_color").append("<option value='" + datas['data_color'][i] + "'>"
                        + datas['data_color'][i] + "</option>");}

                for (var i = 0; i < datas['data_size'].length; i++) {
                    $("#privot_size").append("<option value='" + datas['data_size'][i] + "'>"
                        + datas['data_size'][i] + "</option>");}
                form.render('select');
            }});
    });


    form.on('select(category)', function(data){
        console.log(data.value); //得到被选中的值
        category = data.value;
        $("#privot_style").empty().append("<option value='.*'>选择style</option>");
        $.ajax({
            type: 'get',
            url: "/style_list/?account="+account + '&category=' + category,
            dataType: 'json',
            success: function (datas) {//返回list数据并循环获取
                for (var i = 0; i < datas['data_style'].length; i++) {
                    $("#privot_style").append("<option value='" + datas['data_style'][i] + "'>"
                        + datas['data_style'][i] + "</option>");}

                form.render('select');
            }});
    });
});


function pivot_table_html() {
    $.get('/pivot_table_html/', function (res) {
        $('#pivot_table_html').empty().css("cssText","height:600px !important").html(res['html']);
    })
}
