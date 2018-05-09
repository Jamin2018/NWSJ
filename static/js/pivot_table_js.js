// $(function() {
//     $.ajax({
//         type : 'get',
//         url :"/account-list/",
//         dataType : 'json',
//         success : function(datas) {//返回list数据并循环获取
//             var temp_html ='';
//             for (var i = 0; i < datas['account_list'].length; i++) {
//                 temp_html += "<option value='"+datas['account_list'][i]+"'>"
//                     + datas['account_list'][i] + "</option>";
//             }
//             var a = $("#privot_account").html();
//             console.log(a)
//             layui.use('table',function () {
//                 var table = layui.table();
//                 table.render('select', 'account')
//             })
//             var b = $("#privot_account").html();
//             console.log(b)
//         }
//     });
// });