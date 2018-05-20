var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        heading: 'Administrative Actions',
        landed: false,

        branches: [],
        categories: [],

        loading: 'Loading...',
        branchLoading: '',
        categoryLoading: '',

        error: '',
        message: '',
        bothForms: {
            fields:{
                name: 'empty',
            }
        },
        initModal: {
            onShow: function(){
                var form = $(this).find('.form')
                form.form(app.bothForms)
                form.find('.ui.error.message').empty()
                // consform.form(':input name')
                console.log('clear values')
            },
            onApprove: function(){
                var form = $(this).find('.form')
                $(form).find('.ui.error.message').empty()
                if(!form.form('is valid')){
                    form.form('validate form')
                    return false
                }
                var data = form.form('get values')
                if(!data)
                    return false
                if(data.what === 'category'){
                    app.createCategory(data.name)
                }
                else if (data.what === 'branch'){
                    app.createBranch(data.name)
                }
                return true
            }
        }
    },
    created: function(){
        this.load(['branches', 'categories'],this.afterLoading)
    },
    updated: function(){

    },
    methods: {
        afterLoading: function(){

            var dom = $(this.$el)
            
            dom.find('#afterLanding').show()
            
            dom.find('.ui.modal').modal(this.initModal)
            
            dom.find('.ui.form').form(this.bothForms)

            this.landed = true
        },
        showModal: function(modalid){
            if(!modalid){
                console.log('Invalid modal ID:',modalid)
            }
            console.log('showing modal ',modalid)
            $('#' + modalid).modal('show')
        },
        createCategory: function(name){
            var vm = this
            this.categoryLoading = true
            var postData = {name:name}
            this.$http.post('/api/admin/category/add', postData).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    vm.showToast('Category added', 'success', 'check')
                    vm.categories.push(response.body.category)
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                app.categoryLoading = false
            },
            error => {
                console.log(error)
                app.categoryLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        createBranch: function(name){
            var vm = this
            this.branchLoading = true
            var postData = {name:name}
            this.$http.post('/api/admin/branch/add', postData).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    vm.showToast('Branch added', 'success', 'check')
                    vm.branches.push(response.body.branch)
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                app.branchLoading = false
            },
            error => {
                console.log(error)
                app.branchLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
    },
});