const response = require('cfn-response');
const AWS = require('aws-sdk');
exports.handler = (event, context) => {
    let params = {
        Filters: [
        {
            Name: "tag:aws:cloud9:environment", 
            Values: [
                event.ResourceProperties.EdxProjectCloud9
            ]
        }
        ]
    };
    let ec2 = new AWS.EC2();
    ec2.describeInstances(params, (err, data) => {
        if (err) {
            console.log(err, err.stack); // an error occurred
            response.send(event, context, response.FAILED, response.Data);
        }else{
            let responseData = {Value: data.Reservations[0].Instances[0].SecurityGroups[0].GroupId};        
            console.log(responseData);
            response.send(event, context, response.SUCCESS, responseData);
        }        
    });
};
