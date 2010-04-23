<response>
    <results name=$response.name taxonomyID=$response.taxonomyID since=$response.since  count=$response.count >
    <!-- returns a list of manual annotations of biologically relevant changes stored in a private field at the polypeptide level -->
    #for $result in $response.results:
        <gene 
            change=$result.change 
            date=$result.date 
            feature=$result.feature 
            feature_type=$result.feature_type 
            gene=$result.gene 
            type=$result.type
            />
    #end for
    </results>
</response>