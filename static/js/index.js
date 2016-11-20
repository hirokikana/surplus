var CashbookListItem = React.createClass({
	render: function() {
		return (
			<tr>
				<td>{this.props.use_date}</td>
				<td>{this.props.item}</td>
				<td>{this.props.expense}</td>
			</tr>
		);
	}
});

var request = window.superagent;

var CashBookList = React.createClass({
	getInitialState: function() {
		return {
			itemlist: [ ]
		}
	},

	componentDidMount: function()  {
		request.get("/api/v1/cashbook").end(function(err, res){
			this.setState({itemlist: res.body});
		}.bind(this));
	},
	
	render:function() {
		return (
			<table className="table table-striped table-bordered">
				<thead>
				<tr>
					<th>利用日</th>
					<th>詳細</th>
					<th>支出</th>
				</tr>
				</thead>
				<tbody>
					{this.state.itemlist.map((item) => (<CashbookListItem item={item.item} expense={item.expense} use_date={item.use_date} />))}
				</tbody>
			</table>
		);
	}
});

var m = React.render(<CashBookList />, document.getElementById('app'));

