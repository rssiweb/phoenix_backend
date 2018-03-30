var app = new Vue({
    el: '#app',
    data: {
        heading:'Students Attendance',
        token: Cookies.get('auth_token'),
        is_admin: (Cookies.get('is_admin')=='true'),
        students: [],
        error: '',
        message: '',
        loading: '',
        timeFormat: '',
        attendanceDate: moment(),
        displayDateString: moment().format('dddd, Do MMMM'),
        viewOnly: false,
        nextIsFuture: true,
        categoryFilter: [],
        branchFilter: [],
        editMode: false,
    },
    created: function(){
        console.log('stating')
        this.loadStudents()
    },
    updated: function(){
        $(this.$el).find('table').tablesort();
        $(this.$el).find('.dropdown').dropdown();
        $(this.$el).find('#attendanceDate').calendar({
            type: 'date',
            closable: true,
            onChange: this.setDate,
        });
    },
    methods: {
        logout: function(){
            Cookies.remove('auth_token')
            window.location = '/'
        },
        loadStudents: function(){
            this.loading = 'Loading students...'
            var token = this.token;
            console.log('token', token)
            this.$http.get('/api/student',this.getHeaders())
            .then(data => {
                console.log(data)
                this.students = data.body.students
                if(this.students.length == 0){
                    if(data.body.message)
                        this.message = data.body.message
                    else
                        this.message = 'No students'
                }else{
                    this.message = ''
                }
                console.log(this.message)
                this.loading = ''
                this.getAttendance()
            },error => {
                this.error = error.body.message
                console.log(error)
                this.loading = ''
            });

        },
        getHeaders: function(){
            return {headers: { Authorization: 'Basic ' +  this.token}}
        },
        getAttendance: function(){
            this.loading = 'Loading attendance...'
            var token = this.token
            var vm = this
            var url = '/api/attendance/'+this.attendanceDate.format('DDMMYYYY')
            this.$http.get(url, vm.getHeaders())
            .then(data => {
                console.log(data)
                vm.students.forEach(function(student, stdi){
                    student.in = undefined
                    student.out = undefined
                    student.comment = undefined
                    data.body.attendance.forEach(function(item, index){
                        if(student.id == item.student.id){
                            console.log(student,item,'matched')
                            student.in = item.punchIn
                            student.inby = item.punchInBy
                            student.out = item.punchOut
                            student.outby = item.punchOutBy
                            student.comment = item.comments
                            vm.$set(vm.students, stdi, student)
                        }
                    })
                });
                this.loading = ''
            },error => {
                console.log(error)
                this.loading = ''
                this.message = error.data.message
            });
        },
        savePunchIn(student){
            var updatedStd = student
            updatedStd.inloading = true
            var indexOfStd = this.students.indexOf(student)

            //after clearing the vales if tries to punch in its not able to do so
            if(!this.editMode){
                //when faculty clicks punchIn button
                updatedStd.in = moment().format('HH:mm:ss')
            }else{
                //when admin modifies the punchOut
                if (updatedStd.in == ''){
                    //admin clears the puchIn field
                    if(updatedStd.out){
                        updatedStd.inerror = 'clear punch out before punch in'
                    }
                    else if(updatedStd.comment){
                        updatedStd.inerror = 'cannot clear punch in when comment is present'
                    }
                    else{
                        updatedStd.inerror = ''
                    }
                }else{
                    //admin changes the time in puchIn field
                    var newTime = moment(updatedStd.in,['HH:mm:ss','HH:mm'])
                    
                    if(!newTime.isValid()){
                        updatedStd.inerror = 'Invalid Time'
                    }

                    if(student.out){
                        var tmpOut = moment(student.out,['HH:mm:ss','HH:mm'])
                        if(!newTime.isBefore(tmpOut)){
                            updatedStd.inerror = 'should be before punch out'
                        }
                    }else{
                        updatedStd.in = newTime.format('HH:mm:ss')
                        updatedStd.inerror = ''
                    }
                }
            }
            if(updatedStd.inerror){
                updatedStd.inloading = false
                this.$set(this.students, indexOfStd, updatedStd)
                return
            }
            // to update button states
            this.$set(this.students, indexOfStd, updatedStd)
            this.saveAttendaceData(updatedStd, indexOfStd, 'in')
        },
        savePunchOut(student){

            var updatedStd = student
            updatedStd.outloading = true
            var indexOfStd = this.students.indexOf(student)

            if(updatedStd.out == undefined){
                //when faculty clicks punchOut button
                updatedStd.out = moment().format('HH:mm:ss')
            }
            else{
                //when admin modifies the punchOut
                if (updatedStd.out == ''){
                    //when admin clears the punchOut field
                    //it is a valid case, when admin wants a student to be punched in only
                    updatedStd.outerror = ''
                }else{
                    //when admin changes the time in punchOut field
                    var newTime = moment(updatedStd.out,['HH:mm:ss','HH:mm'])
                    var tmpIn = moment(updatedStd.in,['HH:mm:ss','HH:mm'])
                    if(newTime.isValid() && newTime.isAfter(tmpIn)){
                        updatedStd.out = moment(updatedStd.out,['HH:mm:ss','HH:mm']).format('HH:mm:ss')
                        updatedStd.outerror = ''
                    }else{
                        updatedStd.outerror = 'Invalid Time ' + updatedStd.out
                        if(!newTime.isAfter(tmpIn))
                            updatedStd.outerror = 'Punch out time should be after ' + updatedStd.in
                    }
                }
            }

            if(updatedStd.outerror){    
                updatedStd.outloading = false
                this.$set(this.students, indexOfStd, updatedStd)
                return
            }
            this.$set(this.students, indexOfStd, updatedStd);
            this.saveAttendaceData(updatedStd,indexOfStd, 'out')
        },
        saveComment(student){
            var indexOfStd = this.students.indexOf(student)
            this.saveAttendaceData(student, indexOfStd, 'comment')
        },
        saveAttendaceData: function(updatedStd, stdIndex, what){
            if(what != 'in' && what != 'out' && what != 'comment') return

            var postData = {}

            if(what == 'in'){
                postData.in = updatedStd.in
            }
            else if(what == 'out'){
                postData.out = updatedStd.out
            }
            else if(what == 'comment'){
                postData.comment = updatedStd.comment
            }
            var url = ''
            if(this.editMode)
                url = '/api/admin/attendance/'+this.attendanceDate.format('DDMMYYYY')+'/'+updatedStd.id+'/'+what
            else
                url = '/api/attendance/'+updatedStd.id+'/'+what
            console.log('url',url)
            console.log('postData',postData)
            var vm = this
            //vm.$set(vm.students, stdIndex, updatedStd);
            //ajax request to punch in the student
            vm.$http.post(url, postData, vm.getHeaders())
            .then(response => {
                console.log(response)
                if(response.body.status == 'success'){
                    console.log('saved')
                    if(response.body.attendance){
                        var newupdatedStd = updatedStd
                        newupdatedStd.in    = response.body.attendance.punchIn
                        newupdatedStd.out    = response.body.attendance.punchOut
                        newupdatedStd.inby = response.body.attendance.punchInBy
                        newupdatedStd.outby = response.body.attendance.punchOutBy
                        newupdatedStd.comment = response.body.attendance.comments
                        console.log(newupdatedStd)
                        if(what == 'in')
                            newupdatedStd.inloading = false
                        if(what == 'out')
                            newupdatedStd.outloading = false
                        if(what == 'cooment')
                            newupdatedStd.commentloading = false
                        vm.$set(vm.students, stdIndex, newupdatedStd)
                    }
                }
                else{
                    if(!this.editMode){
                        //case 1 when user is adding the changse
                        // undo the changes in ui
                        var redoUpdatedStd = updatedStd
                        if(what == 'in'){
                            redoUpdatedStd.in = undefined
                            redoUpdatedStd.inloading = false
                        }
                        else if(what == 'out'){
                            redoUpdatedStd.out = undefined
                            redoUpdatedStd.outloading = false
                        }
                        else if(what == 'comment'){
                            redoUpdatedStd.comment = undefined
                            redoUpdatedStd.commentloading = false
                        }
                    } else {
                        //case 2 admin removing the changes
                        // undo the changes in ui
                        var redoUpdatedStd = updatedStd
                        if(what == 'in'){
                            redoUpdatedStd.in = response.body.attendance.punchIn
                            redoUpdatedStd.inloading = false
                        }
                        else if(what == 'out'){
                            redoUpdatedStd.out = response.body.attendance.punchOut
                            redoUpdatedStd.outloading = false
                        }
                        else if(what == 'comment'){
                            redoUpdatedStd.comment = response.body.attendance.comment
                            redoUpdatedStd.commentloading = false
                        }
                    }
                    vm.$set(vm.students, stdIndex, redoUpdatedStd)
                }
            }, error => {
                console.log(error);
                var redoUpdatedStd = updatedStd
                if(what == 'in'){
                    redoUpdatedStd.in = undefined
                    redoUpdatedStd.inloading = false
                }
                if(what == 'out'){
                    redoUpdatedStd.out = undefined
                    redoUpdatedStd.outloading = false
                }
                if(what == 'comment'){
                    redoUpdatedStd.comment = undefined
                    redoUpdatedStd.commentloading = false
                }
                this.$set(this.students, stdIndex, redoUpdatedStd)
            });
        },
        getTimeString: function(datetime){
            if (datetime){
                return moment(datetime,['HH:mm:ss']).format('hh:mm A')
            }
            else{
                return datetime
            }
        },
        nextDay: function(){
            console.log('nextDay')
            this.attendanceDate = moment(this.attendanceDate).add(1, 'day')
            var today = moment()
            if(today.diff(this.attendanceDate,'days')==0)
                this.viewOnly = false
            this.getAttendance()
        },
        previousDay: function(){
            console.log('preDay')
            this.attendanceDate = moment(this.attendanceDate).subtract(1, 'day')
            this.viewOnly = true
            this.getAttendance()
        },
        setDate(date, text, mode){
            console.log('date', date)
            this.attendanceDate = moment(date);
            var today = moment()
            if(today.diff(this.attendanceDate,'days')==0)
                this.viewOnly = false
            else
                this.viewOnly = true
            this.getAttendance()
            return true;
        },
        toggleEditMode: function(){
            this.editMode = !this.editMode
            console.log('editMode',this.editMode)
            if(this.editMode){

            }else{

            }
        },
    },
    watch:{
        token: function(){
            if(!this.token)
                window.location = '/'
        },
        attendanceDate: function(){
            var currAttendance = moment(this.attendanceDate)
            currAttendance.add(1,'day')
            var today = moment()
            this.nextIsFuture = currAttendance.isAfter(today)
            console.log(this.nextIsFuture)
        }
    },
    computed:{
        currentAttendanceDate:function(){
            return this.attendanceDate.format('dddd, Do MMMM YYYY')
        },
        filteredStudents(){
            return this.students.filter(student => {
                var inSearchedCat = this.categoryFilter.length==0 || this.categoryFilter.indexOf(student.category) != -1
                var inSearchedBranch = this.branchFilter.length==0 || this.branchFilter.indexOf(student.branch) != -1
                return inSearchedCat && inSearchedBranch
            })
        },
        categories(){
            var categories=[]
            this.students.forEach((std,index)=>{
                if(categories.indexOf(std.category)==-1)
                    categories.push(std.category)
            })
            return categories;
        },
        branches(){
            var branches=[]
            this.students.forEach((std,index)=>{
                if(branches.indexOf(std.branch)==-1)
                    branches.push(std.branch)
            })
            return branches
        },
        editModeBtnText: function(){
            return this.editMode ? "Done" : "Edit Mode"
        },
    }
});