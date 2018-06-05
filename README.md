# Recruit AI – Integration Guide

Recruit AI can integrate with any ATS that supports a rest API interface for requesting data and iFrame based integration for display of the user interface. Integrating Recruit AI with an ATS therefore involves two distinct pieces of work. API Integration component and an iFrame based HTML/CSS/JS component.

## Design considerations

The Recruit AI engine functions as a black-box, candidates and positions are posted to the system using the routes:

`post /public/candidate`
`post /public/position`

Recommendations are retrieved from the engine using the routes:

`get /public/candidate`
`get /public/position`

Any integration can be done by simply using these 4 routes. This enables a number of scenarios (and combinations of):

Integration performed by Recruit AI tech team
Integration performed by the customer’s development team or 3rd party
Support of the integration components by Recruit AI tech team
Support of the integration components by the customer’s development team or 3rd party
Development of integration components by customer’s  development team or 3rd party
Development of integration components by ATS development team

The flexibility of allowing customers to perform or support their own integration is important as it means they can retain control of what data we are able to access. For example, they can run the integration API component on their own AWS instance meaning they don’t have to provide us with API keys / login access to their ATS. It also enables them to blind the data before feeding it to Recruit AI.

## API Integration component

The API component simply requests data from the ATS rest API interface and feeds it to the Recruit AI rest interface. Recruit AI has two routes available for feeding data:
	
`/public/candidate`
`/public/position`

Further documentation is available here:

https://documenter.getpostman.com/view/4472245/RW8CH82p#0a179430-bb9b-487f-9ae3-da2e47543587

The API integration component will generally work as follows (depending on the ATS)

1. Authenticate with the ATS  rest API
2. Manage a checkpoint- a date/time when data was last requested from the ATS
3. Request Candidate and Position data from the ATS that has been modified since the last checkpoint
4. Parse the data into the correct format to feed to Recruit AI
5. Authenticate with the Recruit AI rest API
6. Post the data to the /public/candidate and /public/position routes


The plan is to build out API components in github for all the ATS we encounter. They will likely follow a similar format to the Bullhorn one and can be cloned/adjusted accordingly.

The API components can be implemented in any language/platform however the recommended standard is to use python targeting Ubuntu 16.04


## iFrame based html/css/js component

An iFrame component is an html file that gets loaded into an iFrame within the ATS. E.g. in Bullhorn when viewing a Candidate screen there is a Positions tab. When clicking on the Positions tab a query is made to the Recruit AI server and an html file is returned and loaded into an iFrame within Bullhorn. This displays the recommended positions for the candidate. The user can then interact within the iFrame to filter results. When the user click on a position, a call will be made from the iFrame to the main Bullhorn frame to navigate the user to the Position screen.

In general the work required to adapt the bullhorn html code for a new ATS will involve:

Formatting the HTML/CSS to match the design standards of the ATS
Making the correct calls to the parent frames to provide navigation

Performing the actual integration will be highly dependent on the ATS and it’s flexibility and security model. With Bullhorn it can all be done from the Admin interface and requires some custom tabs to be created and the correct URLs set for these custom tabs.

### Authenticating with Recruit AI

Authentication with Recruit AI happens via an API Key, which will be issued to the integrator when the instance is created. The token is passed in an http header named “token” in order to authenticate.

Tokens are also issued for iFrame integration  and are passed in the URL via a parameter named “bh”


