Vue.use(Toasted, {
    iconPack : 'fontawesome'
})

var app = new Vue({
    el: '#app',
    data: {
        token: Cookies.get('auth_token'),
        is_admin: (Cookies.get('is_admin')=='true'),
        branches: [],
        categories: [],
        students: [],
        selectedCategories: [],
        selectedBranches: [],
        selectedStudents: [],
        month: '',
        taskCount: 0,
    },
    created(){
        console.log('created')
        this.loadAll()
    },
    updated(){
        console.log('updated')
        var dom = $(this.$el)
        dom.find('.dropdown').dropdown()
        dom.find('#month').calendar({
            type: 'month',
            closable: true,
            maxDate: new Date(),
            onChange: this.setMonth,
        })
    },
    methods: {
        logout: function(){
            Cookies.remove('auth_token')
            window.location = '/'
        },
        getHeaders: function(){
            return {headers: { Authorization: 'Basic ' +  this.token}}
        },
        loadAll(){
            var vm = this
            var branches = undefined
            var categories = undefined
            var students = undefined
            var taskCount = 3
            this.$http.get('/api/branches', this.getHeaders())
            .then(response => {
                console.log(response)
                taskCount -= 1
                if(response.body.status==='success'){
                    branches = response.body.branches
                    if(taskCount == 0){
                        vm.categories = categories
                        vm.branches = branches
                        vm.students = students
                    }
                }
            },
            error => {
                console.log(error)
                taskCount -= 1
            })

            this.$http.get('/api/categories', this.getHeaders())
            .then(response => {
                console.log(response)
                taskCount -= 1
                if(response.body.status==='success'){
                    categories = response.body.categories
                    if(taskCount == 0){
                        vm.categories = categories
                        vm.branches = branches
                        vm.students = students
                    }
                }
            },
            error => {
                console.log(error)
                taskCount -= 1
            })
            this.$http.get('/api/student', this.getHeaders())
            .then(response => {
                console.log(response)
                taskCount -= 1
                if(response.body.status==='Success'){
                    students = response.body.students
                    if(taskCount == 0){
                        vm.categories = categories
                        vm.branches = branches
                        vm.students = students
                    }
                }
            },
            error => {
                console.log(error)
                taskCount -= 1
            })

        },
        toggleStudentSelection(student){
            var index = this.selectedStudents.indexOf(student)
            if(index ==-1){
                this.selectedStudents.push(student)
            } else {
                this.selectedStudents.splice(index, 1)
            }
        },
        setMonth(date, text, mode){
            this.month = moment(date).format('MMMM YYYY')
        },
        exportReport(){
            var vm = this
            var url = '/api/exportReport'
            var students = this.selectedStudents
            if (students.length == 0)
                 students = this.filteredStudents
            studentIds = []
            students.forEach((student) => {
                studentIds.push(student.id)
            })
            vm.month = vm.month || moment().format('MMMM YYYY')
            var postData = {
                month: vm.month,
                students: studentIds,
                categories: vm.selectedCategories,
                branches: vm.selectedBranches,
            }
            console.log(postData)
            var config = this.getHeaders()
            config.responseType = 'blob'
            this.$http.post(url, postData, config)
            .then(response => {
                var blob = new Blob([response.data])
                var link = document.createElement('a')
                link.href = window.URL.createObjectURL(blob)
                link.download = 'Report ' + vm.month + '.jpg'
                link.click()
            },
            error => {
                console.log(error)
            })
        }
    },
    computed: {
        filteredStudents(){
            var vm = this
            return this.students.filter(student => {
                return (vm.selectedCategories.length == 0 || vm.selectedCategories.indexOf(student.category.id) != -1) &&
                       (vm.selectedBranches.length == 0 || vm.selectedBranches.indexOf(student.branch.id) != -1)
            })
        }
    }
})