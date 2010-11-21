<response>
    <error type=$response.error.type code=$response.error.code>
        #filter Filter
        <message>$response.error.message</message>
        #end filter
    </error>
</response>
