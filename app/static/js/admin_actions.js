var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        heading: 'Administrative Actions',
        landed: false,

        branches: [],

        loading: 'Loading...',
        branchLoading: '',

        updateAction: false,

        error: '',
        message: '',
        initBasicForm: {
            fields:{
                name: 'empty',
            }
        },
        initBasicModal: {
            onShow: function(){
                var form = $(this).find('.form')
                form.form(app.initBasicForm)
                form.find('.ui.error.message').empty()
                form.find('.ui.checkbox').checkbox()
            },
            onApprove: function(){
                var form = $(this).find('.form')
                $(form).find('.ui.error.message').empty()
                if(!form.form('is valid')){
                    form.form('validate form')
                    return false
                }
                var data = form.form('get values')
                console.log('form data', data)
                if(!data)
                    return false
                
                else if (data.what === 'branch'){
                    if(app.updateAction){
                        app.updateBranch(data)
                    }else{
                        app.createBranch(data)
                    }
                }
                else{
                    // to stop dialog closing
                    return false
                }
                return true
            }
        },
    },
    created: function(){
        this.loadv2([
            {name:'Branches',
             url:'/api/branch/list',
             variableName: 'branches',
             dataInReponse:'branches'}
             ], this.afterLoading)
        // this.load(['branches', 'categories', 'subjects', 'exams'],this.afterLoading)
    },
    updated: function(){
        // initializing dropdowns and calendar here because when user
        // clicks on 'Add test' button the data changes which leads Vue to call updated
        $('.ui.dropdown').dropdown()
        $('.ui.calendar').calendar({type: 'date'})
    },
    methods: {
        afterLoading: function(){
            var dom = $(this.$el)
            dom.find('#afterLanding').show()
            
            dom.find('#branchModal').modal(this.initBasicModal)
            
            dom.find('.ui.form').form(this.bothForms)

            this.landed = true
        },
        createBranch: function(branch){
            var vm = this
            this.branchLoading = true
            var postData = {name:branch.name}
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
                vm.branchLoading = false
            },
            error => {
                console.log(error)
                vm.branchLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },
        updateBranch(branch){
            console.log(branch)
            branch.id = parseInt(branch.id)
            var vm = this
            this.branchLoading = true
            var postData = {name:branch.name}
            this.$http.post('/api/admin/branch/update/'+branch.id, postData).
            then(response => {
                console.log(response)
                if(response.body.status === 'success'){
                    var updatedBranch = response.body.branch
                    var index = -1
                    vm.branches.forEach((branch, i) => {
                        if(branch.id === updatedBranch.id){
                            index = i
                        }
                    })
                    if(index != -1){
                        vm.$set(vm.branches, index, updatedBranch)
                    }
                    vm.showToast('Successfully updated '+updatedBranch.name, 'success', 'check')
                }else{
                    var message = response.body.error || response.body.message 
                    vm.showToast(message, 'warn', 'close')
                }
                vm.branchLoading = false
            },
            error => {
                console.log(error)
                vm.branchLoading = false
                var msg = error.statusText || 'Something bad happened! Try again'
                vm.showToast(msg, 'warn', 'close')
            })
        },

        showCreateBranch: function(){
            this.updateAction = false
            var form = $('#branchModal').find('.form')
            var formData = {what:'branch'}
            form.form('set values', formData)
            this.showModal('branchModal')
        },
        showUpdateBranch: function(branch){
            this.updateAction = true
            var form = $('#branchModal').find('.form')
            var formData = Object.assign({}, branch)
            formData.what = 'branch'
            form.form('set values', formData)
            this.showModal('branchModal')
        }
    }
});