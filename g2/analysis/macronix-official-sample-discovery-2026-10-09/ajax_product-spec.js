function getProductDetailJsonByPNNo(host, value, menu, pnno, callFunc)
{
	// Getting our list items
	$.ajax({
		url: host + "/_layouts/15/zMacronixPortal2016/getProductDetailJsonByPNNo.aspx?" + "p=" + value + "&m=" + menu + "&n=" + pnno,
		method: "GET",
		headers: { "Accept": "application/json; odata=verbose" },
		success: function (data) {
			// Returning the results
			//console.log(data)
			var jsonData = JSON.parse(data);
			if (jsonData == "empty")
			{
				document.getElementById("DescriptionArea").innerHTML = "";
				document.getElementById("ContentArea").innerHTML = "No Data Found";
			}
			else
			{
				callFunc(jsonData, value);
			}
		},
		error: function (data) {
			document.getElementById("ContentArea").innerHTML = data;
		}
	});
}

function getProductDetailJsonByMenu3(host, value, menu, callFunc)	//IC202500023
{
	// Getting our list items
	$.ajax({
		url: host + "/_layouts/15/zMacronixPortal2016/getProductDetailJsonByMenu3.aspx?" + "p=" + value + "&m=" + menu,
		method: "GET",
		headers: { "Accept": "application/json; odata=verbose" },
		success: function (data) {
			// Returning the results
			//console.log(data)
			var jsonData = JSON.parse(data);
			if (jsonData == "empty")
			{
				document.getElementById("DescriptionArea").innerHTML = "";
				document.getElementById("ContentArea").innerHTML = "No Data Found";
			}
			else
			{
				callFunc(jsonData, value);
			}
		},
		error: function (data) {
			document.getElementById("ContentArea").innerHTML = data;
		}
	});
}

function displayProductDetail(jsonData, selectValue)
{
	var hasPage = false;
	var cnt = 1;		//IC202500023
	$.each(jsonData, function(index, obj){
	
		var desc = getProdIdxContent(obj.ProdIdx);
		document.getElementById("DescriptionArea").innerHTML = desc;
					
		// Specifications
		var content = "";
		content += "<table class='pc_tab pc_word_gray'><tbody>";
		content += getProdSpecContent(obj);
		content += getRecommendedProduct(obj);
		content += "</tbody></table>";
		if (obj.Mode.indexOf("Page") > -1)
		{
			hasPage = true;
		}
		//content += "<p class='pc_note'>" + GetFeature(content, hasPage) + "</p>";
		document.getElementById("ContentArea" + cnt).innerHTML = content;
		$( '#ProductBox' + cnt ).css('display', 'block');
		$( '#ContentArea' + cnt ).css('display', 'block');
		
		// PCN/EOL
		var pcneol = "";
		//if (obj.RecommendedProduct != "" || obj.Notification.length > 0)
		if (obj.Notification.length > 0)
		{
			//if (obj.Menu3.indexOf("Auto") == -1 && obj.Menu3.indexOf("KGD") == -1 )	//remark by 2024050023
			//{
				pcneol += getPCNEOLContent(obj);
				document.getElementById("PcneolArea" + cnt).innerHTML = pcneol;
				$( '#PcneolBox' + cnt ).css('display', 'block');
			//}
		}
		
		// Full EPN	//PM2023008_FullEPN
		var fullepn = "";
		if (obj.FullEPNs.length > 0)
		{
			fullepn += getFullEPNContent(obj);
			document.getElementById("FullEPNArea" + cnt).innerHTML = fullepn;
			$( '#FullEPNBox' + cnt ).css('display', 'block');
		}
		
		
		// Technical Documents
		var techdoc = "<h2 class='pc_mb6'>Technical Documents</h2>";
		if ((obj.AppNote.length > 0 || obj.IBIS.length > 0 || obj.Verilog.length > 0 || obj.LLD.length > 0) && obj.Menu3.indexOf("Auto") == -1 && obj.Menu3.indexOf("KGD") == -1)
		{
			techdoc += getTechDocContent(obj);
			document.getElementById("TechDocArea" + cnt ).innerHTML = techdoc;
			$( '#TechDocBox' + cnt ).css('display', 'block');
		} else {
			if (obj.Menu3.indexOf("KGD") != -1)	//KGD not show technical document section
			{
				
			} else if (obj.Menu3.indexOf("Auto") != -1 || obj.ProdType == "Secure Flash")	//technical document show contact macronix
			{
				document.getElementById("TechDocArea" + cnt ).innerHTML = techdoc + "<table class='pc_tab pc_word_gray'><tbody><tr><td class='pc_td_R' width='20%'>IBIS Models</td><td width='80%'><a class=\"texte\" target=\"_blank\" href=\"" + contactUrl + obj.PartNo + "\">Contact Macronix</a></tr><tr><td class='pc_td_R' width='20%'>Verilog Models</td><td width='80%'><a class=\"texte\" target=\"_blank\" href=\"" + contactUrl + obj.PartNo + "\">Contact Macronix</a></tr><tr><td class='pc_td_R' width='20%'>Low Level Driver</td><td width='80%'><a class=\"texte\" target=\"_blank\" href=\"" + contactUrl + obj.PartNo + "\">Contact Macronix</a></tr></tbody></table>";
			} else {
				document.getElementById("TechDocArea" + cnt ).innerHTML = techdoc + "No Document Found";
			}
		}
		
		//More Software
		$( '#MoreSoftware' + cnt ).attr("href", getMoreSoftwareURL(obj));
		cnt++;
	});
	if (jsonData.length > 1) 
	{
		var statusBar = getStatusBar(jsonData);	//IC202500023		
		document.getElementById("StatusBar" ).innerHTML = statusBar;
		$( '#StatusBar' ).css('display', 'block');
	}
}

function getProdSpecContent(obj)
{
	var ret = "";
	if(isDispMobile) {
		ret = getProdSpecContent_Mobile(obj);
	} else {
		ret = getProdSpecContent_PC(obj);
	}
	return ret;
}

function getProdSpecContent_Mobile(obj)
{
	var ret = "";
	var tmp;
	if (obj.ProdType == "Secure Flash")	//for secure use ProdType, else use MENU3
	{
		tmp = obj.Menu3;
	} else {
		tmp = obj.ProdType;
	}
	switch (tmp)
	{
		case "Serial ROM":
		case "Parallel ROM":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Access Time(ns)</td><td>" + GetBrDisplay2(obj.Speed) + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td></td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Serial NOR":
		case "Serial NOR Flash":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Frequency, MHz (Bus Width)</td><td>" + GetBrDisplay2(obj.Speed) + "</td></tr><tr><td class='pc_td_R'>Feature List</td><td>" + GetBrDisplay(obj.Mode) + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td>" + GetBuyOnline(obj) + "</td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Parallel NOR":
		case "Parallel NOR Flash":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Access Time (ns)</td><td>" + GetBrDisplay2(obj.Speed) + "</td></tr><tr><td class='pc_td_R'>Sector Type</td><td>" + obj.Org + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Feature List</td><td>" + GetBrDisplay(obj.Mode) + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td>" + GetBuyOnline(obj) + "</td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "SLC NAND":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Cell Type</td><td>" + obj.BitsCell + "</td></tr><tr><td class='pc_td_R'>Sequential Read Speed (ns)</td><td>" + obj.Speed + "</td></tr><tr><td class='pc_td_R'>Page Size</td><td>" + obj.PageSize + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>ECC Requirement</td><td>" + obj.ECC + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td>" + GetBuyOnline(obj) + "</td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Serial NAND":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Cell Type</td><td>" + obj.BitsCell + "</td></tr><tr><td class='pc_td_R'>Frequency (MHz)</td><td>" + obj.Speed + "</td></tr><tr><td class='pc_td_R'>Page Size</td><td>" + obj.PageSize + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>ECC Requirement</td><td>" + obj.ECC + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td>" + GetBuyOnline(obj) + "</td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "eMMC":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Cell Type</td><td>" + GetBrDisplay(obj.CellType) + "</td></tr><tr><td class='pc_td_R'>e.MMC Bersion</td><td>" + obj.eMMCversion + "</td></tr><tr><td class='pc_td_R'>Interface Band Width (MB/s)</td><td>" + obj.InterfaceBandWidth + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td>" + GetBuyOnline(obj) + "</td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Serial Managed NAND":
			ret = "<tr><td class='pc_td_R' width='50%'>Density</td><td width='50%'>" + obj.Density + "</td></tr><tr><td class='pc_td_R'>Status</td><td>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Page Size</td><td>" + obj.PageSize + "</td></tr><tr><td class='pc_td_R'>Frequency, MHz (Bus Width)</td><td>" + obj.Speed + "</td></tr><tr><td class='pc_td_R'>Feature List</td><td>" + GetBrDisplay(obj.Mode) + "</td></tr><tr><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td></tr>" + getRecommendedProduct_Mobile(obj) + "<tr><td>" + GetBuyOnline(obj) + "</td><td>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		default:
			ret = "";
			break;
	}

	return ret;
}

function getProdSpecContent_PC(obj)
{
	var ret = "";
	var tmp;
	if (obj.ProdType == "Secure Flash")	//for secure use ProdType, else use MENU3
	{
		tmp = obj.Menu3;
	} else {
		tmp = obj.ProdType;
	}
	switch (tmp)
	{
		case "Serial ROM":
		case "Parallel ROM":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Access Time(ns)</td><td>" + GetBrDisplay2(obj.Speed) + "</td><td class='pc_td_R'>Packages</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Serial NOR":
		case "Serial NOR Flash":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Frequency, MHz (Bus Width)</td><td>" + GetBrDisplay2(obj.Speed) + "</td></tr><tr><td rowspan='2' class='pc_td_R'>Feature List</td><td rowspan='2'>" + getFeatureFullContent(GetBrDisplay(obj.Mode)) + "</td><td class='pc_td_R'>" + getPackagesTitle(obj) + "</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetBuyOnline(obj) + " " + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Parallel NOR":
		case "Parallel NOR Flash":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Access Time (ns)</td><td>" + GetBrDisplay2(obj.Speed) + "</td></tr><tr><td class='pc_td_R'>Sector Type</td><td>" + obj.Org + "</td><td rowspan='2' class='pc_td_R'>" + getPackagesTitle(obj) + "</td><td rowspan='2'>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Feature List</td><td>" + getFeatureFullContent(GetBrDisplay(obj.Mode)) + "</td><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetBuyOnline(obj) + " " + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "SLC NAND":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Cell Type</td><td>" + obj.BitsCell + "</td><td class='pc_td_R'>Sequential Read Speed (ns)</td><td>" + obj.Speed + "</td></tr><tr><td class='pc_td_R'>Page Size</td><td>" + obj.PageSize + "</td><td class='pc_td_R'>" + getPackagesTitle(obj) + "</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>ECC Requirement</td><td>" + obj.ECC + "</td><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetBuyOnline(obj) + " " + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Serial NAND":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Cell Type</td><td>" + obj.BitsCell + "</td><td class='pc_td_R'>Frequency (MHz)</td><td>" + obj.Speed + "</td></tr><tr><td class='pc_td_R'>Page Size</td><td>" + obj.PageSize + "</td><td class='pc_td_R'>" + getPackagesTitle(obj) + "</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>ECC Requirement</td><td>" + obj.ECC + "</td><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetBuyOnline(obj) + " " + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "eMMC":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Cell Type</td><td>" + GetBrDisplay(obj.CellType) + "</td><td class='pc_td_R'>" + getPackagesTitle(obj) + "</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Interface Band Width (MB/s)</td><td>" + obj.InterfaceBandWidth + "</td><td class='pc_td_R' rowspan='2'>Temperature Range</td><td rowspan='2'>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>e.MMC Version</td><td>" + obj.eMMCversion + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetBuyOnline(obj) + " " + GetSampleRequest(obj) + " </td></tr>";
			break;
		case "Serial Managed NAND":
			ret = "<tr><td class='pc_td_R' width='20%'>Density</td><td width='25%'>" + obj.Density + "</td><td class='pc_td_R' width='20%'>Status</td><td width='35%'>" + GetStatusTitle(obj.PartNoStatus) + "</td></tr><tr><td class='pc_td_R'>Vcc</td><td>" + GetVccDisplay(obj.Vcc, obj.VccRange) + "</td><td class='pc_td_R'>Bus Width</td><td>" + obj.IOBus + "</td></tr><tr><td class='pc_td_R'>Page Size</td><td>" + obj.PageSize + "</td><td class='pc_td_R'>Frequency, MHz (Bus Width)</td><td>" + obj.Speed + "</td></tr><tr><td rowspan='2' class='pc_td_R'>Feature List</td><td rowspan='2'>" + getFeatureFullContent(GetBrDisplay(obj.Mode)) + "</td><td class='pc_td_R'>" + getPackagesTitle(obj) + "</td><td>" + GetBrDisplay(obj.Package) + "</td></tr><tr><td class='pc_td_R'>Temperature Range</td><td>" + obj.Grade + "<br/>" + GetBrDisplay(obj.TemperatureRange) + "</td></tr><tr><td class='pc_td_R'>Datasheet</td><td colspan='2'>" + GetDatasheetSpec(obj) +"</a></td><td class='pc_tab_BL'>" + GetBuyOnline(obj) + " " + GetSampleRequest(obj) + " </td></tr>";
			break;
		default:
			ret = "";
			break;
	}

	return ret;
}

//=========================================================================================

function getRecommendedProduct(obj)
{
	var ret = "";
	if(isDispMobile) {
		//ret = getRecommendedProduct_Mobile(obj);
	} else {
		ret = getRecommendedProduct_PC(obj);
	}
	return ret;
}

function getRecommendedProduct_Mobile(obj)
{
	var ret = "";
	var tmp = obj.RecommendedProduct.split("@");
	if (tmp[0] != "")
	{
		ret += "<td class='pc_td_R'>Recommended Product</td><td>";
		if (tmp[0] == "Not Available")
		{
			ret += tmp[0];
		}
		else
		{
			ret += "<a href='" + location.href.replace(/%20/g, " ").replace(obj.PartNo, tmp[0]).replace(obj.PNNo, tmp[1]) + "'>" + tmp[0] + "</a>";
		}
		ret += "</td>";
	}
	return ret;
}

function getRecommendedProduct_PC(obj)
{
	var ret = "";
	var tmp = obj.RecommendedProduct.split("@");
	if (tmp[0] != "")
	{
		ret += "<td class='pc_td_R'>Recommended Product</td><td colspan='2'>";
		if (tmp[0] == "Not Available")
		{
			ret += tmp[0];
		}
		else
		{
			ret += "<a href='" + location.href.replace(/%20/g, " ").replace(obj.PartNo, tmp[0]).replace(obj.PNNo, tmp[1]) + "'>" + tmp[0] + "</a>";
		}
		ret += "</td><td class='pc_tab_BL'></td>";
	}
	return ret;
}

//=========================================================================================

function getPCNEOLContent(obj)
{
	var ret = "";
	if(isDispMobile) {
		ret = getPCNEOLContent_PC(obj);
	} else {
		ret = getPCNEOLContent_PC(obj);
	}
	return ret;
}

/*function getPCNEOLContent_Mobile(obj)
{
	var ret = "";
	ret += "<table class='pc_tab pc_word_gray'><tbody><tr>";
	if (obj.ProdType.indexOf("ROM") == -1)
	{
		ret += "<td class='pc_td_R' width='35%'>Recommended Product</td><td width='65%'>";
		if (obj.RecommendedProduct == "Not Available")
		{
			ret += obj.RecommendedProduct;
		}
		else
		{
			ret += "<a href='" + location.href.replace(obj.PartNo, obj.RecommendedProduct) + "'>" + obj.RecommendedProduct + "</a>";
		}
		ret += "</td>";
	}
	ret += "</tr><tr>";
	ret += "<td class='pc_td_R'>Notification</td><td>";
	if (obj.Notification.length > 0 )
	{
		$.each(obj.Notification, function(index, ndoc){
			ret += "<div class='pdf_group_tab clear-fix'><div class='pdf_group_tab_icon'><img src='/SiteImages/icon_pdf.png'></div><div class='pdf_group_tab_text'><a onclick=\"javascript:_gaq.push(['_trackPageview','/download/Notification/" + ndoc.fName + "']);\" href='/Lists/TechDoc/Attachments/" + ndoc.Id + "/" + ndoc.fName + "' target='_blank'>" + ndoc.fDesc + "</a></div>";
		});
	}
	ret += "</td></tr></tbody></table>";

	return ret;
}*/

function getPCNEOLContent_PC(obj)
{
	var ret = "";
	ret += "<table class='pc_tab pc_word_gray'><tbody><tr>";
	/*if (obj.ProdType.indexOf("ROM") == -1)
	{
		ret += "<td class='pc_td_R' width='20%'>Recommended Product</td><td width='25%'>";
		if (obj.RecommendedProduct == "Not Available")
		{
			ret += obj.RecommendedProduct;
		}
		else
		{
			ret += "<a href='" + location.href.replace(obj.PartNo, obj.RecommendedProduct) + "'>" + obj.RecommendedProduct + "</a>";
		}
		ret += "</td>";
	}*/
	ret += "<td class='pc_td_R' width='20%'>Notification</td><td width='80%' colspan='2'>";
	if (obj.Notification.length > 0 )
	{
		$.each(obj.Notification, function(index, ndoc){
			ret += "<div class='pc_pdf_icon1'><img src='/SiteImages/icon_pdf.png'></div><div class='pc_txt_break'><a onclick=\"javascript:ga('send', 'pageview','/download/Notification/" + ndoc.fName + "');\" href='/Lists/TechDoc/Attachments/" + ndoc.Id + "/" + ndoc.fName + "' target='_blank'>" + ndoc.fDesc + "</a></div>";
		});
	}
	ret += "</td></tr></tbody></table>";

	return ret;
}
//=========================================================================================

function getStatusBar(jsonData)		//IC202500023
{
	var ret = "";
	var cnt = 1;
	$.each(jsonData, function(index, obj){		
		if(isDispMobile) {
			ret += "<a href='#Specifications" + cnt + "'>" + GetStatusBarTitle(obj.PartNoStatus) + "</a>";
		} else {
			ret += "<div class=pc_anchor_3box><a href='#Specifications" + cnt + "'>" + GetStatusBarTitle(obj.PartNoStatus) + "</a></div>";
		}
		cnt++;
	});
	if(isDispMobile) {
		ret += "<div class=pc_anchor_2box>" + ret + "</div>";
	}
	return ret;
}

function getTechDocContent(obj)
{
	var ret = "";
	ret += "<table class='pc_tab pc_word_gray'><tbody>";
	
	if (obj.AppNote.length > 0 && obj.Menu3.indexOf("Temp") == -1 && obj.Menu3.indexOf("Auto") == -1 && obj.Menu3.indexOf("KGD") == -1)
	{
		ret += "<tr><td class='pc_td_R' width='20%'>Application Notes</td><td width='80%'>";
		$.each(obj.AppNote, function(index, sdoc){
			if (index > 0) {ret += "</br>";}
			//ret += "<div><div class='pc_pdf_icon1'><img src='/SiteImages/icon_pdf.png'></div><div class='pc_txt_break'><a href='/Lists/ApplicationNote/Attachments/" + sdoc.Id + "/" + sdoc.fName + "' target='_blank' onclick=\"javascript:ga('send', 'pageview','/download/ApplicationNote/" + sdoc.fName + "');\">" + sdoc.fDesc + "</a></div></div>";
			ret += "<div class='pdf_group_tab clear-fix'><div class='pdf_group_tab_icon'><img src='/SiteImages/icon_pdf.png'></div><div class='pdf_group_tab_text'><a href='/Lists/ApplicationNote/Attachments/" + sdoc.Id + "/" + sdoc.fName + "' target='_blank' onclick=\"javascript:ga('send', 'pageview','/download/ApplicationNote/" + sdoc.fName + "');\">" + sdoc.fDesc + "</a></div></div>";
		});
		ret += "</tr>";
	}
	if (obj.IBIS.length > 0 )
	{
		ret += "<tr><td class='pc_td_R' width='20%'>IBIS Models</td><td width='80%'>";
		$.each(obj.IBIS, function(index, sdoc){
			if (index > 0) {ret += "</br>";}
			//var ibisUrl = "/_layouts/15/zMacronixPortal2016/window/DownloadFile.aspx?FileUrl=" + hostUrl + "/Lists/TechDoc/Attachments/" + sdoc.Id + "/" + sdoc.fName + "&OrginalFileName=" + sdoc.fDesc;
			//var ibisUrl = "/_layouts/15/zMacronixPortal2016/window/DownloadFile.aspx?FileUrl=" + "/Lists/TechDoc/Attachments/" + sdoc.Id + "/" + sdoc.fName + "&OrginalFileName=" + sdoc.fDesc;
			var ibisUrl = "/Lists/TechDoc/Attachments/" + sdoc.Id + "/" + sdoc.fName;
			ret += "<div class='pdf_group_tab clear-fix'><div class='pdf_group_tab_icon'><img src='/SiteImages/zipicon.gif'></div><div class='pdf_group_tab_text'><a href='" + ibisUrl + "' target='_blank' onclick=\"javascript:ga('send', 'pageview','/download/IBIS/" + sdoc.fName + "');\">" + sdoc.fDesc + "</a></div></div>";
		});
		ret += "</tr>";
	}
	if (obj.Verilog.length > 0 )
	{
		ret += "<tr><td class='pc_td_R' width='20%'>Verilog Models</td><td width='80%'>";
		$.each(obj.Verilog, function(index, sdoc){
			if (index > 0) {ret += "</br>";}
			ret += "<div class='pdf_group_tab clear-fix'><div class='pdf_group_tab_icon'><img src='/SiteImages/zipicon.gif'></div><div class='pdf_group_tab_text'><a href='/Lists/TechDoc/Attachments/" + sdoc.Id + "/" + sdoc.fName + "' target='_blank' onclick=\"javascript:ga('send', 'pageview','/download/Verilog/" + sdoc.fName + "');\">" + sdoc.fDesc + "</a></div></div>";
		});
		ret += "</tr>";
	}
	if (obj.LLD.length > 0 )
	{
		ret += "<tr><td class='pc_td_R' width='20%'>Low Level Driver</td><td width='80%'>";
		$.each(obj.LLD, function(index, sdoc){
			if (index > 0) {ret += "</br>";}
			ret += "<div class='pdf_group_tab clear-fix'><div class='pdf_group_tab_icon'><img src='/SiteImages/zipicon.gif'></div><div class='pdf_group_tab_text'><a href='/Lists/TechDoc/Attachments/" + sdoc.Id + "/" + sdoc.fName + "' target='_blank' onclick=\"javascript:ga('send', 'pageview','/download/LLD/" + sdoc.fName + "');\">" + sdoc.fDesc + "</a></div></div>";
		});
		ret += "</tr>";
	}
	
	ret += "</tbody></table>";

	return ret;

}

function getFullEPNContent(obj)	//PM2023008_FullEPN
{
	var ret = "";
	var hasRecommendEPN = false;
	
	$.each(obj.FullEPNs, function(index, sdoc){
		if (sdoc.RecommendEPN != "")
		{
			hasRecommendEPN = true;
		}
	});
	
	ret += "<table class='pc_tab pc_word_gray'><tbody>";
	if (hasRecommendEPN) {
		ret += "<tr class='pc_head'><td width='15%'>Full Part No.</td><td width='15%'>Package</td><td width='15%'>Temperature Range</td><td width='15%'>Product Status</td><td width='15%'>Recommended</td><td width='5%'></td><td width='5%'></td></tr>";
	} else {
		ret += "<tr class='pc_head'><td width='15%'>Full Part No.</td><td width='15%'>Package</td><td width='15%'>Temperature Range</td><td width='15%'>Product Status</td><td width='5%'></td><td width='5%'></td></tr>";
	}
	$.each(obj.FullEPNs, function(index, sdoc){
		if(index % 2 == 0)
		{
			ret += "<tr class='pc_oddNU'>";
		} else {
			ret += "<tr class='pc_evenNU'>";
		}
		if (hasRecommendEPN) {
			ret += "<td nowrap>" + sdoc.FullEPN + "</td><td nowrap>" + GetBrDisplay(sdoc.Package) + "</td><td nowrap>" + sdoc.Grade + "<br/>" + GetBrDisplay(sdoc.TemperatureRange) + "</td><td nowrap>" + GetStatusTitle(sdoc.FullEPNStatus) + "</td>"
			if (sdoc.RecommendEPNKey == null) {	
				ret += "<td nowrap>" + sdoc.RecommendEPN + "</td>";
			} else {
				//RecommendEPN on web
				if (location.host.indexOf('www-') != -1 ){
					ret += "<td nowrap><a href='" + window.location.pathname + "?s=" + sdoc.RecommendEPNKey.split("@")[0] + "&m=" + sdoc.RecommendEPNKey.split("@")[1] + "&n=" + sdoc.RecommendEPNKey.split("@")[2] + "'>" + sdoc.RecommendEPN + "</a></td>";
				} else {
					ret += "<td nowrap><a href='" + window.location.pathname + "?p=" + sdoc.RecommendEPNKey.split("@")[0] + "&m=" + sdoc.RecommendEPNKey.split("@")[1] + "&n=" + sdoc.RecommendEPNKey.split("@")[2] + "'>" + sdoc.RecommendEPN + "</a></td>";
				}
			}
			ret += "<td nowrap>" + GetFullEPNBuyOnline(obj, sdoc) + "</td><td nowrap>" + GetFullEPNSampleRequest(sdoc) + "</td>";
			
		} else {
			//no RecommendEPN
			ret += "<td nowrap>" + sdoc.FullEPN + "</td><td nowrap>" + GetBrDisplay(sdoc.Package) + "</td><td nowrap>" + sdoc.Grade + "<br/>" + GetBrDisplay(sdoc.TemperatureRange) + "</td><td nowrap>" + GetStatusTitle(sdoc.FullEPNStatus) + "</td><td nowrap>" + GetFullEPNBuyOnline(obj, sdoc) + "</td><td nowrap>" + GetFullEPNSampleRequest(sdoc) + "</td>";
		}
		ret += "</tr>";
	});
	ret += "</tbody></table>";

	return ret;
}

function getProdIdxContent(ProdIdx)
{
	var ret = "";
	switch (ProdIdx)
	{
		case "1":
			ret = "The MX25xxx06 series provides Standard Serial Interface x1 or x2 I/O, Single I/O or Dual I/O, at a single 3V or 2.5V power-supply voltage. These products are offered in 4KB sectors and 64KB blocks structures for individual erase usage.";
			break;
		case "2":
			ret = "The Default Lock Protection Series is optimized for parameter protection applications with demands for block-lock protection by a volatile protection bit in the selected design boot area used by the BP bits, against Program and Erase instructions in a protected area. ";
			break;
		case "3":
			ret = "Macronix Serial Multi I/O (MXSMIO™) Flash provides not only Single I/O, but also Multi-I/O interfaces. MX25/66_3x/72/73 series offer Dual I/O or Quad I/O operations which double or quadruple the read performance of systems for high-end consumer applications. In this series, MX25_72/73 series provide Multi-I/O default enable solution that quad mode read instruction can be executed directly without the configuration of Quad Enable register, along with the supports of single and dual mode commands. The Multi-I/O interface is available without any setting in the Flash side, and it provides user with a more convenient way to experience the Multi-I/O performance.";
			break;
		case "4":
			ret = "The MXSMIO™ Duplex (DTR) Series family offers not only Single I/O, but also Quad I/O interface with Double Transfer Rate (DTR) mode operation providing fast data transfer rate up to 400MHz, which makes it the fastest serial NOR Flash in the industry. In this series, MX25/66_41/71/79/89/91/93/94 series provide Multi-I/O default enable solution that quad mode read instruction can be executed directly without the configuration of Quad Enable register, along with the supports of single and dual mode commands. The Multi-I/O interface is available without any setting in Flash side, and it provides user more convenient way to experience the Multi-I/O performance.";
			break;
		case "5":
			ret = "The Standard Read Access Parallel Flash products (MX29F and MX29LV) are offered in Boot and Uniform Sector architectures in x8, x16, and x8/x16 configurations in 5V and 3V.";
			break;
		case "6":
			ret = "The MX29GL/MX68GL Page Mode Read Access enhanced performance products are offered in densities from 32Mb through 1 Gb.";
			break;
		case "7":
			ret = "As the leader of Serial NOR Flash provider, Macronix provides a full line support of Serial Interface Secure Flash products. Customers could enjoy the benefits of low pin-count, high throughput of Macronix Serial NOR Flash while taking advantage of the security features such as the permanent sector protection, read protection, etc. The Secure Flash products are used in applications like Set-Top Boxes, Digital TVs and other systems requiring security of their code and data and also saving the pin-counts in the systems.";
			break;
		case "8":
			ret = "To facilitate customers who have sensitive data stored in their systems on flash memory and have a need to prevent unauthorized access, Macronix provides Standard Interface Secure Parallel Flash product series to help in fulfilling the customers’ needs. The Parallel Secure Flash not only features the functionalities of Macronix Parallel Flash but also provides the security features such as sector protection, permanent sector lock, password protection, data encryption. The Parallel Secure Flash is available from 32Mb to 512Mb and is used in applications like Set-Top Boxes, Digital TVs and other systems requiring security of their codes and data.";
			break;
		case "9":
			ret = "";
			break;
		case "10":
			ret = "The MX30LF and MX60LF families, compliant with ONFI 1.0, consist of 3V SLC NAND Flash memory available in various densities. The MX30UF family offers 1.8V SLC NAND Flash memory across a range of densities as well. Both the 3V and 1.8V SLC NAND Flash product lines deliver high performance and reliability, making them ideal for data and code storage. The MX30LF 3V family is well-suited for embedded applications, such as TVs, set-top boxes, digital cameras, IPCs, and industrial systems. Meanwhile, the MX30UF 1.8V family is designed for embedded applications including mobile phones, 3G/4G data cards, M2M devices, and more.";
			break;
		case "11":
			ret = "The MX29NS is a single-bank, burst mode product with Address-Data Multiplexing (AD-Mux). Densities available are 32Mb, 64Mb and 128Mb.";
			break;
		case "12":
			ret = "The MX29VS is a multi-bank, burst mode product with simultaneous read-write and Address-Data Multiplexing (AD-Mux). This product is currently available in 128Mb.";
			break;
		case "13":
			ret = "Macronix provides a complete range of serial NAND Flash solutions with mainstream SPI interfaces. These include different voltages (3V & 1.8V), various densities, and standard packages, with some densities also available in smaller 6x5mm packages. Featuring high-speed performance and continuous read capability, these products perfectly meet the requirements of various applications such as industrial systems, access-point routers, smart speakers, digital TVs, set-top boxes, and surveillance systems.";
			break;
		case "14":
			ret = "Macronix e•MMC™ product family is an embedded flash memory which is fully compatible with the JEDEC e•MMC™ 5.1 standard. It is a managed flash solution for variety of electronic devices such as smartphones, tablets, digital TVs, set-top boxes and network devices. The e•MMC™ product integrates the Macronix MLC NAND device and controller chip as a multi-chip module, with a standard interface protocol to the host system.";
			break;
		case "15":
			ret = "The MX31 family consists of both 1.8V and 3V high-density serial flash memory devices that support a special NOR-like booting feature in Single, Dual, and Quad I/O operations. The MX31LF is the 3V Serial NAND family, while the MX31UF is the 1.8V version, offering a performance of 104MHz SPI clock rate in Quad I/O mode. Some systems require an SPI NAND device but still need to adopt an SPI NOR for booting. LybraFlash now offers a more efficient design that provides designers with the cost benefits of gigabit flash capacity while allowing booting without the need to add an additional SPI NOR.";
			break;
		case "16":
			ret = "Macronix provides a complete range of serial NAND Flash solutions with mainstream SPI interfaces. These include different voltages (3V & 1.8V), various densities, and standard packages, with some densities also available in smaller 6x5mm packages. Featuring high-speed performance and continuous read capability, these products perfectly meet the requirements of various applications such as industrial systems, access-point routers, smart speakers, digital TVs, set-top boxes, and surveillance systems.";
			break;
		case "17":
			ret = "MX75/78 ArmorFlash memory is a highly secure data-storage solution for a wide range of markets, such as IoT, automotive, computing, industrial, healthcare, wearables, smart homes, and smart cities. It supports standard SPI, QSPI, and OctaBus interfaces. ArmorFlash ensures data confidentiality, integrity, and availability, offering high levels of security with features like Physical Unclonable Function (PUF) and unique ID with authenticated and encrypted links for NOR, SLC NAND, or e.MMC™ flash memory. It provides highly configurable memory partitions depending on the needs of the system. MX75 provides secure area for Authentication/Encryption/Decryption and Authenticated Data Read/Write with MAC, and Symmetric key AES256, while MX78 provides secure area for AES Authentication/Encryption/Decryption, Asymmetric key ECDH, ECC & CRC.";
			break;
		case "18":
			ret = "MX76 ArmorBoot is designed for authenticating flash memory, performing secure boot and secure updates, and enabling system integrity. It features a standard SPI interface and simple command interface. Monotonic counters are included to prevent rollback attacks. ArmorBoot also has features like ECC and Physical Unclonable Function (PUF) for unique IDs. ArmorBoot addresses two important security functions that any embedded system needs. First is authentication. When the system is booting, the host can verify through an attestation scheme that the memory device is valid. Second, for systems that utilize SecureBoot, instead of exposing the code to the external SPI bus during this process, ArmorBoot keeps it internal to the device, verifying the integrity of what is stored. It then indicates to the host the results. If there is a mismatch in any digital signatures, the system can default to device recovery software. ArmorBoot flash memory is ideal for any embedded design for applications, such as IoT, industrial automation, and automotive electronics.";
			break;
		case "19":
			ret = "Macronix Serial Multi I/O (MXSMIO™) Flash provides not only Single I/O, but also Multi-I/O interfaces. The MX77U/L series supports the authentication function by Monotonic Counter (MC) Feature. For Quad I/O Permanent Enable feature, please refer to the Feature List on the individual RPMC product pages.";
			break;
		case "20":
			ret = "Macronix Serial Multi I/O (MXSMIO™) Flash provides not only Single I/O, but also Multi-I/O interfaces. The MX77U/L series supports the authentication function by Monotonic Counter (MC) Feature. The MX77U/Lxxx55 series supports the Permanent Lock feature, while MX77U/Lxxx55G MXSMIO™ DTR family offers not only Single I/O, but also Quad I/O interface with Double Transfer Rate (DTR) mode operation providing fast data transfer rate. For Quad I/O Permanent Enable feature, please refer to the Feature List on the individual RPMC product pages.";
			break;
		case "21":
			ret = "The MXSMIO™ Duplex (DTR) Series family offers not only Single I/O, but also Quad I/O interface with Double Transfer Rate (DTR) mode operation providing fast data transfer rate. Macronix OctaBus Memory (8 I/O) retains the user interface compatible with the ordinary single I/O Serial NOR Flash, which can sustain users' experience in using Serial NOR Flash with minimum efforts. LM/UM series dedicates to raising the frequency, combining with the JEDEC (JESD251-xSPI) compliant DDR (8D-8D-8D) mode. The data transfer rate has therefore been increased, while the read latency has also been lowered immensely. The improved performance will help system in running eXecute In Place (XIP) on OctaFlash with more efficiency and shorten the access time in high density, which accelerates overall system performance. MX25/66UM/UWxxx345G/80G supports DOPI Data output format for Byte Mode data sequence.";
			break;
		case "22":
			ret = "The MXSMIO™ Duplex (DTR) Series family offers not only Single I/O, but also Quad I/O interface with Double Transfer Rate (DTR) mode operation providing fast data transfer rate. OctaFlash (8 I/O) efficiently broaden our Serial NOR Flash throughput. Macronix OctaBus Memory (8 I/O) also retains the user interface compatible with the ordinary single I/O Serial NOR Flash. This breakthrough product incorporates ﬂash memory and RAM memory into the same data I/O bus, reducing the pin count to 12. LW/UW series is a multiple bank architecture based on ultra-high performance OctaBus interface; provide concurrent operation capability that enhance the system performance while data update. It is an ideal solution for Over-The-Air (OTA) update applications which are becoming more prevalent within Automotive and IOT solutions. MX25/66UM/UWxxx345G/80G supports DOPI Data output format for Byte Mode data sequence.";
			break;
			
		default:
			ret = "";
			break;
	}

	return ret;
}

function GetDatasheetSpec(li)
{
	if (li.Attachments == true)
	{
		
		//return "<div class='pc_pdf_icon1'><a onclick=\"javascript:ga('send', 'pageview','/download/Datasheet/" + li.Datasheet + "');\" href=\"/Lists/Datasheet/Attachments/" + li.Id + "/" + li.Datasheet + "\" target='_blank'><img src='/SiteImages/icon_pdf.png'></div><div class='pc_txt_break'>" + li.Datasheet + "</a></div>";
		return "<div class='pdf_group_tab clear-fix'><div class='pdf_group_tab_icon'><a onclick=\"javascript:ga('send', 'pageview','/download/Datasheet/" + li.Datasheet + "');\" href=\"/Lists/Datasheet/Attachments/" + li.Id + "/" + li.Datasheet + "\" target='_blank'><img src='/SiteImages/icon_pdf.png'></a></div><div class='pc_text_break'><a onclick=\"javascript:ga('send', 'pageview','/download/Datasheet/" + li.Datasheet + "');\" href=\"/Lists/Datasheet/Attachments/" + li.Id + "/" + li.Datasheet + "\" target='_blank'>" + li.Datasheet + "</a></div></div>";
		
	}
	else
	{
		return "<a class=\"texte\" target=\"_blank\" href=\"" + contactUrl + li.PartNo + "\">Contact Macronix</a>";
	}
}

function GetBuyOnline(li)
{
	if (li.Buy == "Y" && li.Menu3.indexOf("Auto") == -1 && li.Menu3.indexOf("Temp") == -1 && li.Menu3.indexOf("KGD") == -1 && li.ProdType.indexOf("Secure") == -1)
	{
		//return "<button type='button' class='btn_red3' onclick=\"javascript:window.open('/_layouts/15/zMacronixPortal2016/window/BuyOnline.aspx?PartNo=" + li.PartNo + "&ItemID=" + li.Id + "','newwin','height=400, width=500, toolbar=no, menubar=no, scrollbars=no, resizable=no,location=n o, status=no'); _gaq.push(['_trackEvent', 'Buy Product', 'Clicked', '" + li.PartNo + "']); \">Buy Online</button>";
		//return "<button type='button' class='btn_red3' onclick=\"javascript:window.open('" + buyonlineUrl + "?PartNo=" + li.PartNo + "&ItemID=" + li.Id + "','newwin','height=400, width=500, toolbar=no, menubar=no, scrollbars=no, resizable=no,location=n o, status=no'); _gaq.push(['_trackEvent', 'Buy Product', 'Clicked', '" + li.PartNo + "']); \">Buy Online</button>";
		return "<button type='button' class='btn_red3' onclick=\"javascript:window.open('" + buyonlineUrl + "?PartNo=" + li.PartNo + "','newwin','height=400, width=500, toolbar=no, menubar=no, scrollbars=no, resizable=no,location=n o, status=no'); gtag('event', 'Clicked', {  event_category: 'BuyProduct',  event_label: '" + li.PartNo + "'}); \">Buy Online</button>";
		
	}
	else return "";
}

function GetFullEPNBuyOnline(li, sdoc)	//li=ds obj, sdoc=fullEPN obj	//PM2023008_FullEPN
{
	if (sdoc.FullEPNStatus.indexOf("P") != -1 && li.Menu3.indexOf("Auto") == -1 && li.Menu3.indexOf("Temp") == -1 && li.Menu3.indexOf("KGD") == -1 && li.ProdType.indexOf("Secure") == -1)
	{
		return "<button type='button' class='btn_red3' onclick=\"javascript:window.open('" + buyonlineUrl + "?PartNo=" + sdoc.FullEPN + "','newwin','height=400, width=500, toolbar=no, menubar=no, scrollbars=no, resizable=no,location=n o, status=no'); gtag('event', 'Clicked', {  event_category: 'BuyProduct',  event_label: '" + sdoc.FullEPN + "'}); \">Buy Online</button>";
	}
	else return "";
}

function GetSampleRequest(li)
{
	if (li.PartNoStatus.split(':')[1] != "E")
	{
		return "<button type='button' class='btn_red3' onclick=\"javascript:window.open('" + sampleUrl + li.PartNo + "|&cp=Enter Part No.')\" >Request Sample</button>";
	}
	else return "";
}

function GetFullEPNSampleRequest(li)	//li=fullEPN obj	//PM2023008_FullEPN
{
	if (li.FullEPNStatus.split(':')[1] != "E")
	{
		return "<button type='button' class='btn_red3' onclick=\"javascript:window.open('" + sampleUrl + li.FullEPN + "|&cp=Enter Part No.')\" >Request Sample</button>";
	}
	else return "";
}

function QueryString(name) {
	var AllVars = window.location.search.substring(1);
	var Vars = AllVars.split("&");
	for (i = 0; i < Vars.length; i++) {
		var Var = Vars[i].split("=");
		if (Var[0] == name) return Var[1];
	}
	return "";
}

function getMoreSoftwareURL(li)
{
	var ret = "";
	if(isDispMobile) {
		ret = GetLocaleUrl(location.href) + "/support/technical-documentation/Pages/default.aspx";
	} else {
		ret = GetLocaleUrl(location.href) + "/support/Pages/Design-Support.aspx";	//GC202200005
		/*ret = GetLocaleUrl(location.href) + "/support/technical-documentation/Pages/";
		switch (li.ProdType)
		{
			case "Serial NOR":
			case "Serial NOR Flash":
				ret += "Serial-NOR-Flash.aspx";
				break;
			case "Parallel NOR":
			case "Parallel NOR Flash":
				ret += "Parallel-NOR-Flash.aspx";
				break;
			case "Serial NAND":
			case "Serial NAND Flash":
				ret += "Serial-NAND-Flash.aspx";
				break;
			case "SLC NAND":
			case "SLC NAND Flash":
				ret += "SLC-NAND-Flash.aspx";
				break;
			case "Serial ROM":
			case "Parallel ROM":
				ret += "ROM.aspx";
				break;
			default:
				ret += "Serial-NOR-Flash.aspx";
				break;
		}*/
	}
	return ret;
}

function getPackagesTitle(li)
{
	var ret = "";
	if (li.Menu3 == "KGD")
	{
		ret = "Form Factor";
	} else {
		ret = "Packages";
	}
	return ret;
}

function getFeatureFullContent(content)
{
	var ret = content;
	ret = ret.replace("8 x I/O", "Octa I/O Peripheral Interface");
	ret = ret.replace("PUF", "Physical Unclonable Function");
	ret = ret.replace("DTR", "Double Transfer Rate");
	ret = ret.replace("QPI", "Quad I/O Peripheral Interface");
	ret = ret.replace("Super Low Power", "Super Low Power Consumption");
	ret = ret.replace("Ultra Low Power", "Ultra Low Power Consumption");
	ret = ret.replace("RWW", "Read-While-Write (RWW)");
	ret = ret.replace("Fast Boot", "Fast Boot by Execute in Place(XIP)");
	ret = ret.replace("Suspend/Resume", "Suspend / Resume for Program/Erase");
	ret = ret.replace("Burst Read", "Burst Read with Wrapping");
	ret = ret.replace("V I/O", "Versatile I/O Voltage ");
	ret = ret.replace("Advanced Protection", "Advanced Block/Sector Protection");
	ret = ret.replace("Extended BP Area", "Extended Block Protection Area");
	ret = ret.replace("Specific BP", "Specific BP Block Protection Area");
	ret = ret.replace("Unique ID", "Unique ID stored in flash");
	ret = ret.replace("General (OctaRAM)", "General OctaRAM Feature");
	ret = ret.replace("L/H Switch Bit", "Low Power / High Performance Switch Bit");	//2023080006 add
	

	return ret;
}

function GetStatusBarTitle(status)	//IC202500023
{
	var ret = "";
	var tmps = status;
	if (status.indexOf(":") != -1)
	{
		tmps = status.split(':')[1];
	}
	switch (tmps)
	{
		case "D":
		case "UD":
			ret = "Under Development";
			break;
		case "S":
			ret = "Sampling, for new design";
			break;
		case "P+":
			ret = "Production, for new design";
			break;
		case "P":
			ret = "Production";
			break;
		case "CM":
			ret = "Contact Macronix";
			break;
		case "P-":
			ret = "Not recommend for new design";
			break;
		case "E+":
			ret = "EOL issued";
			break;
		case "E":
			ret = "End of Life";
			break;
	}
	return ret + " Product";
}


if (QueryString("p") != ""){
	var partno = QueryString("p");
	var menu = QueryString("m");
	var pnno = QueryString("n");
	//getProductDetailJsonByPNNo(hostUrl, partno, menu, pnno, displayProductDetail);
	getProductDetailJsonByMenu3(hostUrl, partno, menu, displayProductDetail);		//IC202500023
	
} else if (QueryString("s") != ""){
	var partno = QueryString("s");
	var menu = QueryString("m");
	var pnno = QueryString("n");
	//getProductDetailJsonByPNNo(hostUrl, partno, menu, pnno, displayProductDetail);
	getProductDetailJsonByMenu3(hostUrl, partno, menu, displayProductDetail);		//IC202500023
}