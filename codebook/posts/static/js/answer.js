function CommentViewModel(data) {
    var self = this;
    self.commentId = data['id'];
    self.author = new AuthorViewModel(data['author']);
    self.content = data['content'];
    self.datePublished = data['created'];

    self.remove = remove;

    //-----

    function remove() {
        $.ajax({
            url: RESTAPI_URLS.COMMENTS + self.commentId + '/',
            method: METHODS.DELETE,
        });
    }

    return self;
}

function AnswerViewModel(data) {
    var self = this;
    self.answerId = data['id'];
    self.author = new AuthorViewModel(data['author']);
    self.votes = ko.observable(data['votes']);
    self.content = data['content'];
    self.datePublished = data['created'];
    self.voted = ko.observable(null);
    self.isTopAnswer = data['is_top_answer'];
    self.comments = ko.observableArray([]);
    self.newCommentContent = ko.observable('');

    self.upvote = upvote;
    self.downvote = downvote;
    self.remove = remove;
    self.addComment = addComment;
    self.removeComment = removeComment;

    init();

    //------------

    function init() {
        $.ajax({
            url: RESTAPI_URLS.ANSWERS + self.answerId + RESTAPI_URLS.VOTE,
            method: METHODS.GET,
        }).done(function(data) {
            self.voted(data['vote'] || null);
        });

        $.ajax({
            url: RESTAPI_URLS.ANSWERS + self.answerId + '/comments/',
            method: METHODS.GET,
        }).done(function(data) {
            data.forEach(function(comment) {
                self.comments.push(new CommentViewModel(comment));
            });
        });
    }

    function upvote() {
        var url = RESTAPI_URLS.ANSWERS + self.answerId + RESTAPI_URLS.UPVOTE;
        $.ajax({
            url: url,
            method: METHODS.POST,
        }).done(function(data) {
            self.votes(data['total_votes'])
            self.voted('up');
        });
    }

    function downvote() {
        var url = RESTAPI_URLS.ANSWERS + self.answerId + RESTAPI_URLS.DOWNVOTE;
        $.ajax({
            url: url,
            method: METHODS.POST,
        }).done(function(data) {
            self.votes(data['total_votes'])
            self.voted('down');
        });
    }

    function remove() {
        $.ajax({
            url: RESTAPI_URLS.ANSWERS + self.answerId + '/',
            method: METHODS.DELETE,
        });
    }

    function addComment(author) {
        if (!self.newCommentContent()) {
            return;
        }
        $.ajax({
            url: RESTAPI_URLS.COMMENTS,
            data: {
                'author': author,
                'content': self.newCommentContent(),
                'answer': self.answerId,
            },
            method: METHODS.POST,
        }).done(function(data) {
            $.ajax({
                url: RESTAPI_URLS.COMMENTS + data['id'] + '/',
                method: METHODS.GET,
            }).done(function(data){
                self.newCommentContent('');
                self.comments.push(new CommentViewModel(data));
            });
        });
    }

    function removeComment(comment) {
        comment.remove();
        self.comments.remove(comment);
    }
}


ko.components.register('answer-component', {
    template: { element: 'answer-template' },
    viewModel: AnswerViewModel
});
