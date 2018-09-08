var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        branches: [],
        categories: [],
        students: [],
        exams: [],

        selectedCategories: [],
        selectedBranches: [],
        selectedStudents: [],
        
        selectedBranch: undefined,
        selectedExam: undefined,

        month: moment().format('DD MMMM YYYY'),
        loading: false,
        taskCount: 0,
        error: '',

        initialized: false,

        summaryMonthInitData: {
            type: 'month',
            closable: true,
            maxDate: new Date(),
            onChange: function(date, text, mode){
                return app.setMonth(date, text, mode)
            },
        },
        detailStartMonthInitData: {
            type: 'date',
            closable: true,
            maxDate: new Date(),
            onChange: function(date, text, mode){
                $('#detailEndMonth').calendar('set startDate', date)
                return app.setMonth(date, text, mode)
            },
        },
        detailEndMonthInitData: {
            type: 'date',
            closable: true,
            maxDate: new Date(),
            onChange: function(date, text, mode){
                return app.setEndMonth(date, text, mode)
            },
        },
        summaryReportModalInit: {
            onShow: function(){
                $('#summaryMonth').calendar(app.summaryMonthInitData)
            }
        },
        detailReportModalInit: {
            onShow: function(){
                $('#detailStartMonth').calendar(app.detailStartMonthInitData)
                $('#detailEndMonth').calendar(app.detailEndMonthInitData)
            }
        }
    },
    created(){
        console.log('created')
        this.loadv2([
            {name:'Categories',
             url:'/api/category/1/list',
             variableName: 'categories',
             dataInReponse: 'categories'},
            {name:'Branches',
             url:'/api/branch/list',
             variableName: 'branches',
             dataInReponse: 'branches'},
            {name:'Students',
             url: '/api/student/' + this.month.replace(/ /g,'') + '/all',
             variableName: 'students',
             dataInReponse: 'students'},
             ])
    },
    updated(){
        console.log('updated')
        if(!this.initialized && !this.loading){
            console.log('initialized')
            var dom = $(this.$el)
            dom.find('table').tablesort()
            dom.find('.dropdown').dropdown()
            dom.find('#month').calendar(this.monthInitData)
            dom.find('#attendanceReportModal').modal(this.summaryReportModalInit)
            dom.find('#detailedAttendaceModal').modal(this.detailReportModalInit)
            this.initialized = true
        }
    },
    watch: {
        month(){
            console.log('fetch students', this.month)
            this.loadv2([
                {name:'Students',
                 url: '/api/student/' + this.month.replace(/ /g,'') + '/all',
                 variableName: 'students',
                 dataInReponse: 'students'},
                ])
        },
        selectedBranch: function(){
            this.loadv2([
            {name:'Exams',
             url:'/api/exam/'+this.selectedBranch+'/list',
             variableName: 'exams',
             dataInReponse: 'exams'}
             ])
        }
    },
    methods: {
        toggleStudentSelection(student){
            var index = this.selectedStudents.indexOf(student)
            if(index ==-1){
                this.selectedStudents.push(student)
            } else {
                this.selectedStudents.splice(index, 1)
            }
        },
        setMonth(date, text, mode){
            this.month = moment(date).format('DD MMMM YYYY')
            console.log('setting month', this.month)
        },
        setEndMonth: function(date, text, mode){
            console.log('end date set to', date)
        },
        requestExamReport: function(){
            var vm = this
            vm.loading = true
            var url = '/api/report/generate/exam/' + this.selectedExam
            this.$http.get(url)
            .then(response => {
                if(response.body.status==='success'){
                    vm.showToast(response.body.message, 'success')
                }else{
                    vm.showToast('Request failed! try again', 'warn')
                }
                console.log(response)
                vm.loading = false
            },
            error =>{
                console.log(error)
                this.error = 'Request failed! please re-load the page and try again, if problem still persists please report to admin.'
                vm.showToast(this.error, 'error')
                vm.loading = false
            })
        },
        requestAttendanceReport(){
            this.loading = true
            this.error = ''
            var vm = this
            var url = '/api/report/generate/attendance'
            var students = this.selectedStudents
            if (students.length == 0)
                students = this.filteredStudents
            studentIds = []
            students.forEach((student) => {
                studentIds.push(student.id)
            })
            vm.month = vm.month || moment().format('DD MMMM YYYY')
            var postData = {
                month: vm.month,
                students: studentIds,
                categories: vm.selectedCategories,
                branches: vm.selectedBranches,
            }
            this.$http.post(url, postData)
            .then(response => {
                if(response.body.status === 'success'){
                    vm.showToast(response.body.message, 'success')
                }else{
                    vm.showToast('Request failed! try again', 'warn')
                }
                console.log(response)
                vm.loading = false
            },
            error => {
                this.loading = false
                this.error = 'Request failed! please re-load the page and try again, if problem still persists please report to admin.'
                vm.showToast(this.error, 'error')
                console.log(error)
            })
        },
        requestMarksheetReport: function(){
            var vm = this
            vm.loading = true
            this.$http.get('/api/report/generate/marksheet/' + this.selectedExam)
            .then(response => {
                if(response.body.status==='success'){
                    vm.showToast(response.body.message, 'success')
                }else{
                    vm.showToast('Request failed! try again', 'warn')
                }
                console.log(response)
                vm.loading = false
            },
            error =>{
                console.log(error)
                this.error = 'Request failed! please re-load the page and try again, if problem still persists please report to admin.'
                vm.showToast(this.error, 'error')
                vm.loading = false
            })
        },
        showAttendanceModal: function(){
            $('#attendanceReportModal').modal('show')
        },
        showDetailedAttendanceModal: function(){
            $('#detailedAttendaceModal').modal('show')
        },
        showResultModal: function(){
            $('#resultModal').modal('show')
        },
        showMarksSheetModal: function(){
            $('#marksheetModal').modal('show')
        },
        requestGenerateICard: function(){
            var data = $('#ICardModal .form').form('get values')
            console.log(data)
            this.$http.get('/api/report/generate/card/' + data.branch)
        }
    },
    computed: {
        filteredStudents(){
            var vm = this
            return this.students.filter(student => {
                return (vm.selectedCategories.length == 0 || vm.selectedCategories.indexOf(student.category) != -1) &&
                (vm.selectedBranches.length == 0 || vm.selectedBranches.indexOf(student.branch) != -1)
            })
        }
    }
})